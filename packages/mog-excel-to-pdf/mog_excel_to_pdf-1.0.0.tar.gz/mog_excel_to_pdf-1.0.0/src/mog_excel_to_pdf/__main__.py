
import os
import sys
import time
import argparse
import tomllib  # Python 3.11+
import pythoncom
import win32com.client as win32
from win32com.client import gencache, constants
import logging
import glob
from pathlib import Path
from pypdf import PdfWriter, PdfReader

INVALID_CHARS = r'\\/:*?"<>|'

def load_toml(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)

def sanitize_filename(name: str, default: str = "まとめ.pdf") -> str:
    if not name:
        return default
    base = "".join(c if c not in INVALID_CHARS else "_" for c in name).strip().rstrip(".")
    return base if base.lower().endswith(".pdf") else base + ".pdf"

def get_excel_app(max_tries: int = 6, delay_sec: float = 0.5):
    """
    Excel の COM を安定して取得する。RPC_E_CALL_REJECTED をリトライし、
    EnsureDispatch が失敗したら DispatchEx にフォールバック。
    """
    pythoncom.CoInitialize()
    for _ in range(max_tries):
        try:
            return gencache.EnsureDispatch("Excel.Application")
        except Exception:
            time.sleep(delay_sec)
    for _ in range(max_tries):
        try:
            return win32.DispatchEx("Excel.Application")
        except Exception:
            time.sleep(delay_sec)
    raise RuntimeError(
        "Excel の COM を取得できませんでした。Excel を閉じ、"
        "`python -m win32com.client.makepy` で Microsoft Excel Object Library を生成し、再試行してください。"
    )

def setup_logger(log_path: str) -> logging.Logger:
    """
    標準出力とログファイルの両方へ「同一文字列」を出力するロガーを作成。
    """
    logger = logging.getLogger("excel_grouped_to_pdf")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(message)s")  # 文字列のみ（時刻やレベルは付けない）

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)

    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger

def normalize_excel_paths(excel_path_cfg) -> list[str]:
    """
    excel_path_cfg が:
      - 文字列: 単一ファイルまたはグロブパターン
      - リスト: 複数ファイル（グロブ対応）
    結果として、存在するファイルのパスをリストで返す。
    """
    paths = []
    cfg_list = [excel_path_cfg] if isinstance(excel_path_cfg, str) else excel_path_cfg
    for pattern in cfg_list:
        matched = glob.glob(pattern)
        if matched:
            paths.extend(sorted(matched))
        else:
            # グロブマッチなし → 直接パスとして扱う
            paths.append(pattern)
    return paths

def merge_pdfs(pdf_paths: list[str], output_path: str, logger: logging.Logger):
    """
    複数の PDF を指定順序で1つのPDFにマージ。
    """
    writer = PdfWriter()
    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
            logger.info(f"マージ: {pdf_path}")
        except Exception as e:
            logger.info(f"警告: {pdf_path} のマージに失敗しました: {e}")
    with open(output_path, "wb") as f:
        writer.write(f)

def resolve_target_sheets(
    wb,
    sheets_cfg,
    exclude_cfg: list[str],
    logger: logging.Logger,
    sort_sheets: bool = False,
    exclude_suffixes: list[str] | None = None,
) -> list[str]:
    """
    sheets_cfg が:
      - リスト: その並びで存在するシートのみ
      - 文字列 "all": 全シート
    それ以外（None/空）はエラー。
    さらに exclude_cfg に一致するシート名を除外する（完全一致）。
    sort_sheets が True の場合、辞書順にソート。
    """
    all_sheet_names = [s.Name for s in wb.Worksheets]

    # 基本の対象決定
    if isinstance(sheets_cfg, list):
        target = []
        for nm in sheets_cfg:
            if nm in all_sheet_names:
                target.append(nm)
            else:
                logger.info(f"警告: 指定シートが見つかりません -> {nm}")
        if not target:
            raise RuntimeError("sheets に指定されたシートが1つも有効ではありません。名前を確認してください。")
    elif isinstance(sheets_cfg, str) and sheets_cfg.strip().lower() == "all":
        target = all_sheet_names[:]  # 全シート
    else:
        raise RuntimeError("設定ファイルに 'sheets' がありません。リストまたは \"all\" を指定してください。")

    # 除外の適用（完全一致）
    exclude_cfg = exclude_cfg or []
    excluded_present = []
    excluded_missing = []
    if exclude_cfg:
        target_set = set(target)
        for nm in exclude_cfg:
            if nm in target_set:
                excluded_present.append(nm)
                target_set.remove(nm)
            else:
                excluded_missing.append(nm)
        target = [nm for nm in target if nm in target_set]

        if excluded_present:
            logger.info(f"除外: {', '.join(excluded_present)}")
        if excluded_missing:
            logger.info(f"参考（指定されたが対象外/存在しない）: {', '.join(excluded_missing)}")

    # サフィックスによる除外（後方一致）
    suffixes = exclude_suffixes or []
    if suffixes:
        filtered = []
        dropped = []
        for nm in target:
            if any(nm.endswith(suf) for suf in suffixes):
                dropped.append(nm)
            else:
                filtered.append(nm)
        if dropped:
            logger.info(f"サフィックス除外: {', '.join(dropped)}")
        target = filtered

    # 辞書順でソート
    if sort_sheets:
        target = sorted(target)
        logger.info(f"辞書順でソート: {', '.join(target)}")

    return target

def process_excel_to_pdf(config: dict, logger=None) -> Path:
    """
    設定辞書から Excel ファイルを PDF に変換する。
    
    Args:
        config: TOML から読み込んだ設定辞書
        logger: ロガー（省略時は setup_logger で生成）
    
    Returns:
        生成された PDF ファイルのパス
    """
    # --- 設定値の取得 ---
    sheets_cfg = config.get("sheets", "all")
    exclude_cfg = config.get("exclude_sheets", [])
    pdf_filename = config.get("pdf_filename", "まとめ.pdf")
    open_after_publish = config.get("open_after_publish", False)
    include_hidden = config.get("include_hidden", True)
    sort_sheets = config.get("sort_sheets", False)
    excel_path_cfg = config.get("excel_path")
    exclude_suffixes = config.get("exclude_suffixes", [])
    output_dir = config.get("output_dir", None)
    log_file = config.get("log_file", None)

    if not excel_path_cfg:
        raise RuntimeError("設定に 'excel_path' がありません。対象 Excel ファイルのパスを指定してください。")

    # Excel ファイルパスのリスト化と存在確認
    excel_paths = normalize_excel_paths(excel_path_cfg)
    for path in excel_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Excel ファイルが見つかりません: {path}")

    # 最初の Excel ファイルのディレクトリを既定出力先に
    default_outdir = os.path.dirname(os.path.abspath(excel_paths[0]))
    outdir = os.path.abspath(output_dir or default_outdir)
    os.makedirs(outdir, exist_ok=True)

    out_pdf = os.path.join(outdir, sanitize_filename(pdf_filename))
    log_path = os.path.abspath(log_file or os.path.join(outdir, "excel_grouped_to_pdf.log"))
    
    if logger is None:
        logger = setup_logger(log_path)

    logger.info(f"Excel ファイル: {', '.join(excel_paths)}")
    logger.info(f"出力PDF: {out_pdf}")
    logger.info(f"ログ: {log_path}")
    logger.info(f"include_hidden: {include_hidden}")

    excel_app = get_excel_app()
    excel_app.Visible = False
    excel_app.DisplayAlerts = False

    # 複数ファイルの場合、全ファイルを1つのワークブックに統合してから1回のPDF出力
    # (ページ番号が正しく振られるため)
    main_wb = None
    copied_sheets = []  # コピーしたシートを記録
    all_selectable = []  # 全ファイルからの選択可能シート
    original_visibility = {}  # 全シートの可視状態
    
    try:
        # 複数ファイルの場合、最初のファイルをベースに他のファイルのシートをコピー
        if len(excel_paths) > 1:
            logger.info(f"\n--- 複数ファイルを統合してPDF化 ---")
            
            # 最初のファイルを開く
            main_wb = excel_app.Workbooks.Open(os.path.abspath(excel_paths[0]))
            
            # 最初のファイルのシートを処理
            logger.info(f"\n--- ファイル 1/{len(excel_paths)}: {excel_paths[0]} ---")
            target_names = resolve_target_sheets(
                main_wb,
                sheets_cfg,
                exclude_cfg,
                logger,
                sort_sheets=False,
                exclude_suffixes=exclude_suffixes,
            )
            logger.info(f"対象シート: {', '.join(target_names) if target_names else '(なし)'}")
            
            for nm in target_names:
                sh = main_wb.Worksheets(nm)
                vis = sh.Visible
                original_visibility[nm] = vis
                if vis != constants.xlSheetVisible:
                    if include_hidden:
                        sh.Visible = constants.xlSheetVisible
                        logger.info(f"一時可視化: {nm}")
                    else:
                        logger.info(f"スキップ（隠しシート）: {nm}")
                        continue
                all_selectable.append(nm)
            
            # 2番目以降のファイルのシートをコピー
            for idx in range(1, len(excel_paths)):
                excel_path = excel_paths[idx]
                logger.info(f"\n--- ファイル {idx + 1}/{len(excel_paths)}: {excel_path} ---")
                src_wb = None
                try:
                    src_wb = excel_app.Workbooks.Open(os.path.abspath(excel_path))
                    target_names = resolve_target_sheets(
                        src_wb,
                        sheets_cfg,
                        exclude_cfg,
                        logger,
                        sort_sheets=False,
                        exclude_suffixes=exclude_suffixes,
                    )
                    logger.info(f"対象シート: {', '.join(target_names) if target_names else '(なし)'}")
                    
                    for nm in target_names:
                        src_sh = src_wb.Worksheets(nm)
                        vis = src_sh.Visible
                        
                        if vis != constants.xlSheetVisible:
                            if include_hidden:
                                src_sh.Visible = constants.xlSheetVisible
                                logger.info(f"一時可視化: {nm}")
                            else:
                                logger.info(f"スキップ（隠しシート）: {nm}")
                                continue
                        
                        # シートを main_wb の最後にコピー
                        src_sh.Copy(After=main_wb.Worksheets(main_wb.Worksheets.Count))
                        copied_sheet = main_wb.Worksheets(main_wb.Worksheets.Count)
                        copied_name = copied_sheet.Name
                        if exclude_suffixes and any(copied_name.endswith(suf) for suf in exclude_suffixes):
                            logger.info(f"サフィックス一致のためコピー後に除外: {copied_name}")
                            # 不要なシートは即座に削除
                            try:
                                copied_sheet.Delete()
                            except Exception:
                                pass
                        else:
                            copied_sheets.append(copied_name)
                            original_visibility[copied_name] = vis
                            all_selectable.append(copied_name)
                            logger.info(f"シートをコピー: {nm} → {copied_name}")
                
                finally:
                    if src_wb is not None:
                        src_wb.Close(SaveChanges=False)
                        # COM負荷軽減のため少し待機
                        time.sleep(0.3)
            
            # 全体で辞書順ソート
            if sort_sheets and len(all_selectable) > 1:
                all_selectable = sorted(all_selectable)
                logger.info(f"全体を辞書順でソート: {', '.join(all_selectable)}")
            
            logger.info(f"\n対象シート（全体、順序どおり）: {', '.join(all_selectable) if all_selectable else '(なし)'}")
            
            # シートの順序を並べ替え
            original_positions = {}
            if len(all_selectable) > 1:
                for sheet_name in all_selectable:
                    sheet = main_wb.Worksheets(sheet_name)
                    original_positions[sheet_name] = sheet.Index
                
                for target_pos, sheet_name in enumerate(all_selectable, start=1):
                    sheet = main_wb.Worksheets(sheet_name)
                    if sheet.Index != target_pos:
                        if target_pos == 1:
                            sheet.Move(Before=main_wb.Worksheets(1))
                        else:
                            sheet.Move(After=main_wb.Worksheets(target_pos - 1))
            
            # シートを選択してPDF出力
            if len(all_selectable) == 1:
                main_wb.Worksheets(all_selectable[0]).Select()
            else:
                main_wb.Worksheets(all_selectable).Select()
            
            excel_app.ActiveSheet.ExportAsFixedFormat(
                Type=constants.xlTypePDF,
                Filename=out_pdf,
                Quality=constants.xlQualityStandard,
                IncludeDocProperties=True,
                IgnorePrintAreas=False,
                OpenAfterPublish=False
            )
            logger.info(f"PDF を出力しました: {out_pdf}")
        
        # 単一ファイルの場合
        else:
            excel_path = excel_paths[0]
            logger.info(f"\n--- ファイル 1/1: {excel_path} ---")
            main_wb = excel_app.Workbooks.Open(os.path.abspath(excel_path))

            # 対象シートの決定
            target_names = resolve_target_sheets(
                main_wb,
                sheets_cfg,
                exclude_cfg,
                logger,
                sort_sheets=sort_sheets,
                exclude_suffixes=exclude_suffixes,
            )
            logger.info(f"対象シート（順序どおり）: {', '.join(target_names) if target_names else '(なし)'}")

            # 非表示シートを一時可視化
            for nm in target_names:
                sh = main_wb.Worksheets(nm)
                vis = sh.Visible
                original_visibility[nm] = vis
                if vis != constants.xlSheetVisible:
                    if include_hidden:
                        sh.Visible = constants.xlSheetVisible
                        logger.info(f"一時可視化: {nm}")
                    else:
                        logger.info(f"スキップ（隠しシート）: {nm}")
                        continue
                all_selectable.append(nm)

            if not all_selectable:
                logger.info(f"警告: {excel_path} でグループ選択できるシートがありません")
            else:
                # 辞書順ソートが有効な場合、シートの順序を並べ替える
                original_positions = {}
                if sort_sheets and len(all_selectable) > 1:
                    for sheet_name in all_selectable:
                        sheet = main_wb.Worksheets(sheet_name)
                        original_positions[sheet_name] = sheet.Index
                    
                    for target_pos, sheet_name in enumerate(all_selectable, start=1):
                        sheet = main_wb.Worksheets(sheet_name)
                        if sheet.Index != target_pos:
                            if target_pos == 1:
                                sheet.Move(Before=main_wb.Worksheets(1))
                            else:
                                sheet.Move(After=main_wb.Worksheets(target_pos - 1))
                
                # シートを選択
                if len(all_selectable) == 1:
                    main_wb.Worksheets(all_selectable[0]).Select()
                else:
                    main_wb.Worksheets(all_selectable).Select()
                
                excel_app.ActiveSheet.ExportAsFixedFormat(
                    Type=constants.xlTypePDF,
                    Filename=out_pdf,
                    Quality=constants.xlQualityStandard,
                    IncludeDocProperties=True,
                    IgnorePrintAreas=False,
                    OpenAfterPublish=False
                )
                logger.info(f"PDF を出力しました: {out_pdf}")

        if open_after_publish:
            try:
                os.startfile(out_pdf)
                logger.info(f"PDF を開きました: {out_pdf}")
            except Exception as e:
                logger.info(f"生成後の自動オープンに失敗: {e}")
    
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise
    
    finally:
        # コピーしたシートを削除
        if main_wb is not None and copied_sheets:
            try:
                for sheet_name in copied_sheets:
                    try:
                        main_wb.Worksheets(sheet_name).Delete()
                        logger.info(f"コピーしたシートを削除: {sheet_name}")
                    except Exception:
                        pass
            except Exception:
                pass
        
        # 可視状態を復元
        if main_wb is not None:
            try:
                for nm, vis in original_visibility.items():
                    try:
                        main_wb.Worksheets(nm).Visible = vis
                    except Exception:
                        pass
            except Exception:
                pass
        
        # ワークブックを閉じる
        if main_wb is not None:
            try:
                main_wb.Close(SaveChanges=False)
            except Exception:
                pass
        
        # Excelアプリを終了
        if excel_app is not None:
            excel_app.Quit()
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            # COM解放の猶予を延長
            time.sleep(1.0)
    
    return Path(out_pdf)

def main():
    parser = argparse.ArgumentParser(
        description="Excel の複数シートをグループ選択して 1 つの PDF に出力。設定ファイルから全て読み込みます。Python 3.11+ 前提。"
    )
    parser.add_argument("config", help="TOML 設定ファイル（例：config.txt / config.toml）")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args()

    cfg = load_toml(args.config)
    
    # ロガーを作成
    output_dir = cfg.get("output_dir", None)
    excel_path_cfg = cfg.get("excel_path")
    if excel_path_cfg:
        excel_paths = normalize_excel_paths(excel_path_cfg)
        default_outdir = os.path.dirname(os.path.abspath(excel_paths[0]))
        outdir = os.path.abspath(output_dir or default_outdir)
    else:
        outdir = os.path.abspath(output_dir or ".")
    
    log_file = cfg.get("log_file", None)
    log_path = os.path.abspath(log_file or os.path.join(outdir, "excel_grouped_to_pdf.log"))
    logger = setup_logger(log_path)
    
    logger.info(f"設定: {os.path.abspath(args.config)}")
    
    process_excel_to_pdf(cfg, logger)

if __name__ == "__main__":
    main()
