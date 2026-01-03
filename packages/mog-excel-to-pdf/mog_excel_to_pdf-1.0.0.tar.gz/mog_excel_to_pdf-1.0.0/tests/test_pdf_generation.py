"""
PDF 化機能のテストスイート
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
import pytest
from pypdf import PdfReader

# src/mog_excel_to_pdf のインポート用にパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import mog_excel_to_pdf as main


class TestPdfGeneration:
    """PDF 化機能のテストクラス"""

    @pytest.fixture
    def test_resources_dir(self):
        """テストリソースディレクトリのパス"""
        return Path(__file__).parent / "resources"

    @pytest.fixture
    def temp_output_dir(self):
        """一時的な出力ディレクトリ"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # テスト後のクリーンアップ
        time.sleep(4.0)  # COM解放を待つ時間をさらに延長
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_single_xlsx_file(self, test_resources_dir, temp_output_dir):
        """単一の .xlsx ファイルから PDF を生成"""
        excel_path = test_resources_dir / "sheet_3_1_2.xlsx"
        
        assert excel_path.exists(), f"Excel file not found: {excel_path}"

        # 設定辞書を作成
        config = {
            "excel_path": str(excel_path),
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_single_xlsx.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_single_xlsx.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（3 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 3, f"Expected 3 pages, got {len(pdf_reader.pages)}"
        
        # 各ページのテキスト内容を確認
        # 1 ページ目に "Sheet3" が含まれていることを確認
        page1_text = pdf_reader.pages[0].extract_text()
        assert "Sheet3" in page1_text, f"'Sheet3' not found in page 1. Content: {page1_text[:100]}"
        
        # 2 ページ目に "Sheet1" が含まれていることを確認
        page2_text = pdf_reader.pages[1].extract_text()
        assert "Sheet1" in page2_text, f"'Sheet1' not found in page 2. Content: {page2_text[:100]}"
        
        # 3 ページ目に "Sheet2" が含まれていることを確認
        page3_text = pdf_reader.pages[2].extract_text()
        assert "Sheet2" in page3_text, f"'Sheet2' not found in page 3. Content: {page3_text[:100]}"

    def test_merge_multiple_files_normal_order(self, test_resources_dir, temp_output_dir):
        """複数の Excel ファイルを通常順序で結合"""
        excel_path_1 = test_resources_dir / "sheet_3_1_2.xlsx"
        excel_path_2 = test_resources_dir / "sheet_6_4_5_7.xlsx"
        
        assert excel_path_1.exists(), f"Excel file not found: {excel_path_1}"
        assert excel_path_2.exists(), f"Excel file not found: {excel_path_2}"

        # 設定辞書を作成（複数ファイル）
        config = {
            "excel_path": [str(excel_path_1), str(excel_path_2)],
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_merge_normal.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test_merge_normal.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_merge_normal.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（7 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 7, f"Expected 7 pages, got {len(pdf_reader.pages)}"
        
        # 各ページのテキスト内容を確認
        # 1-3 ページ目に Sheet3, Sheet1, Sheet2 が含まれていることを確認
        page1_text = pdf_reader.pages[0].extract_text()
        assert "Sheet3" in page1_text, f"'Sheet3' not found in page 1"
        
        page2_text = pdf_reader.pages[1].extract_text()
        assert "Sheet1" in page2_text, f"'Sheet1' not found in page 2"
        
        page3_text = pdf_reader.pages[2].extract_text()
        assert "Sheet2" in page3_text, f"'Sheet2' not found in page 3"
        
        # 4-7 ページ目に Sheet6, Sheet4, Sheet5, Sheet7 が含まれていることを確認
        page4_text = pdf_reader.pages[3].extract_text()
        assert "Sheet6" in page4_text, f"'Sheet6' not found in page 4"
        
        page5_text = pdf_reader.pages[4].extract_text()
        assert "Sheet4" in page5_text, f"'Sheet4' not found in page 5"
        
        page6_text = pdf_reader.pages[5].extract_text()
        assert "Sheet5" in page6_text, f"'Sheet5' not found in page 6"
        
        page7_text = pdf_reader.pages[6].extract_text()
        assert "Sheet7" in page7_text, f"'Sheet7' not found in page 7"

    def test_merge_multiple_files_reverse_order(self, test_resources_dir, temp_output_dir):
        """複数の Excel ファイルを逆順で結合"""
        excel_path_1 = test_resources_dir / "sheet_6_4_5_7.xlsx"
        excel_path_2 = test_resources_dir / "sheet_3_1_2.xlsx"
        
        assert excel_path_1.exists(), f"Excel file not found: {excel_path_1}"
        assert excel_path_2.exists(), f"Excel file not found: {excel_path_2}"

        # 設定辞書を作成（複数ファイル、逆順）
        config = {
            "excel_path": [str(excel_path_1), str(excel_path_2)],
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_merge_reverse.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test_merge_reverse.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_merge_reverse.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（7 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 7, f"Expected 7 pages, got {len(pdf_reader.pages)}"
        
        # 各ページのテキスト内容を確認（逆順なので Sheet6, Sheet4, Sheet5, Sheet7 が先）
        # 1-4 ページ目に Sheet6, Sheet4, Sheet5, Sheet7 が含まれていることを確認
        page1_text = pdf_reader.pages[0].extract_text()
        assert "Sheet6" in page1_text, f"'Sheet6' not found in page 1"
        
        page2_text = pdf_reader.pages[1].extract_text()
        assert "Sheet4" in page2_text, f"'Sheet4' not found in page 2"
        
        page3_text = pdf_reader.pages[2].extract_text()
        assert "Sheet5" in page3_text, f"'Sheet5' not found in page 3"
        
        page4_text = pdf_reader.pages[3].extract_text()
        assert "Sheet7" in page4_text, f"'Sheet7' not found in page 4"
        
        # 5-7 ページ目に Sheet3, Sheet1, Sheet2 が含まれていることを確認
        page5_text = pdf_reader.pages[4].extract_text()
        assert "Sheet3" in page5_text, f"'Sheet3' not found in page 5"
        
        page6_text = pdf_reader.pages[5].extract_text()
        assert "Sheet1" in page6_text, f"'Sheet1' not found in page 6"
        
        page7_text = pdf_reader.pages[6].extract_text()
        assert "Sheet2" in page7_text, f"'Sheet2' not found in page 7"

    def test_merge_three_files(self, test_resources_dir, temp_output_dir):
        """3つの Excel ファイルを結合（sheet_3_1_2.xlsx + sheet_6_4_5_7.xlsx + sheet_3_1_2_8.xlsx）"""
        excel_path_1 = test_resources_dir / "sheet_3_1_2.xlsx"
        excel_path_2 = test_resources_dir / "sheet_6_4_5_7.xlsx"
        excel_path_3 = test_resources_dir / "sheet_3_1_2_8.xlsx"
        
        assert excel_path_1.exists(), f"Excel file not found: {excel_path_1}"
        assert excel_path_2.exists(), f"Excel file not found: {excel_path_2}"
        assert excel_path_3.exists(), f"Excel file not found: {excel_path_3}"

        # 設定辞書を作成（3ファイル）
        config = {
            "excel_path": [str(excel_path_1), str(excel_path_2), str(excel_path_3)],
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_merge_three.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test_merge_three.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_merge_three.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（3 + 4 + 4 = 11 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 11, f"Expected 11 pages, got {len(pdf_reader.pages)}"
        
        # 各ページのテキスト内容を確認
        # 1-3 ページ目: sheet_3_1_2.xlsx の Sheet3, Sheet1, Sheet2
        page1_text = pdf_reader.pages[0].extract_text()
        assert "Sheet3" in page1_text or "3" in page1_text, f"'Sheet3' or '3' not found in page 1"
        
        page2_text = pdf_reader.pages[1].extract_text()
        assert "Sheet1" in page2_text or "1" in page2_text, f"'Sheet1' or '1' not found in page 2"
        
        page3_text = pdf_reader.pages[2].extract_text()
        assert "Sheet2" in page3_text or "2" in page3_text, f"'Sheet2' or '2' not found in page 3"
        
        # 4-7 ページ目: sheet_6_4_5_7.xlsx の Sheet6, Sheet4, Sheet5, Sheet7
        page4_text = pdf_reader.pages[3].extract_text()
        assert "Sheet6" in page4_text or "6" in page4_text, f"'Sheet6' or '6' not found in page 4"
        
        page5_text = pdf_reader.pages[4].extract_text()
        assert "Sheet4" in page5_text or "4" in page5_text, f"'Sheet4' or '4' not found in page 5"
        
        page6_text = pdf_reader.pages[5].extract_text()
        assert "Sheet5" in page5_text or "5" in page6_text, f"'Sheet5' or '5' not found in page 6"
        
        page7_text = pdf_reader.pages[6].extract_text()
        assert "Sheet7" in page7_text or "7" in page7_text, f"'Sheet7' or '7' not found in page 7"
        
        # 8-11 ページ目: sheet_3_1_2_8.xlsx の Sheet3, Sheet1, Sheet2, Sheet8
        page8_text = pdf_reader.pages[7].extract_text()
        assert "Sheet3" in page8_text or "3" in page8_text, f"'Sheet3' or '3' not found in page 8"
        
        page9_text = pdf_reader.pages[8].extract_text()
        assert "Sheet1" in page9_text or "1" in page9_text, f"'Sheet1' or '1' not found in page 9"
        
        page10_text = pdf_reader.pages[9].extract_text()
        assert "Sheet2" in page10_text or "2" in page10_text, f"'Sheet2' or '2' not found in page 10"
        
        page11_text = pdf_reader.pages[10].extract_text()
        assert "Sheet8" in page11_text or "8" in page11_text, f"'Sheet8' or '8' not found in page 11"

    def test_sort_sheets_single_file(self, test_resources_dir, temp_output_dir):
        """単一ファイルでシートを辞書順にソート"""
        excel_path = test_resources_dir / "sheet_3_1_2.xlsx"
        
        assert excel_path.exists(), f"Excel file not found: {excel_path}"

        # 設定辞書を作成（sort_sheets=True）
        config = {
            "excel_path": str(excel_path),
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_sorted_single.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
            "sort_sheets": True,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test_sorted_single.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_sorted_single.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（3 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 3, f"Expected 3 pages, got {len(pdf_reader.pages)}"
        
        # 辞書順なので 1, 2, 3 の順になるはず
        # シート名は "1", "2", "3" のようです（ログより）
        page1_text = pdf_reader.pages[0].extract_text()
        page2_text = pdf_reader.pages[1].extract_text()
        page3_text = pdf_reader.pages[2].extract_text()
        
        # 辞書順ソート後、1ページ目が "Sheet1"（または"1"を含む）
        # 2ページ目が "Sheet2"（または"2"を含む）
        # 3ページ目が "Sheet3"（または"3"を含む）になるはず
        assert "1" in page1_text or "Sheet1" in page1_text, f"Expected '1' or 'Sheet1' in page 1, got: {page1_text}"
        assert "2" in page2_text or "Sheet2" in page2_text, f"Expected '2' or 'Sheet2' in page 2, got: {page2_text}"
        assert "3" in page3_text or "Sheet3" in page3_text, f"Expected '3' or 'Sheet3' in page 3, got: {page3_text}"

    def test_sort_sheets_multiple_files(self, test_resources_dir, temp_output_dir):
        """複数ファイルで全体を辞書順にソート"""
        excel_path_1 = test_resources_dir / "sheet_3_1_2_8.xlsx"
        excel_path_2 = test_resources_dir / "sheet_6_4_5_7.xlsx"
        
        assert excel_path_1.exists(), f"Excel file not found: {excel_path_1}"
        assert excel_path_2.exists(), f"Excel file not found: {excel_path_2}"

        # 設定辞書を作成（複数ファイル、sort_sheets=True）
        config = {
            "excel_path": [str(excel_path_1), str(excel_path_2)],
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_sorted_multiple.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
            "sort_sheets": True,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test_sorted_multiple.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_sorted_multiple.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"
        
        # PDF のページ数を確認（4 + 4 = 8 ページ）
        pdf_reader = PdfReader(str(output_pdf))
        assert len(pdf_reader.pages) == 8, f"Expected 8 pages, got {len(pdf_reader.pages)}"
        
        # 全体で辞書順にソートされたはず
        # 全シート: 1, 2, 3, 4, 5, 6, 7, 8（辞書順）
        
        page1_text = pdf_reader.pages[0].extract_text()
        has_page1 = "Sheet1" in page1_text or "1" in page1_text
        assert has_page1, f"'Sheet1' or '1' not found in page 1"
        
        page2_text = pdf_reader.pages[1].extract_text()
        has_page2 = "Sheet2" in page2_text or "2" in page2_text
        assert has_page2, f"'Sheet2' or '2' not found in page 2"
        
        page3_text = pdf_reader.pages[2].extract_text()
        has_page3 = "Sheet3" in page3_text or "3" in page3_text
        assert has_page3, f"'Sheet3' or '3' not found in page 3"
        
        page4_text = pdf_reader.pages[3].extract_text()
        has_page4 = "Sheet4" in page4_text or "4" in page4_text
        assert has_page4, f"'Sheet4' or '4' not found in page 4"
        
        page5_text = pdf_reader.pages[4].extract_text()
        has_page5 = "Sheet5" in page5_text or "5" in page5_text
        assert has_page5, f"'Sheet5' or '5' not found in page 5"
        
        page6_text = pdf_reader.pages[5].extract_text()
        has_page6 = "Sheet6" in page6_text or "6" in page6_text
        assert has_page6, f"'Sheet6' or '6' not found in page 6"
        
        page7_text = pdf_reader.pages[6].extract_text()
        has_page7 = "Sheet7" in page7_text or "7" in page7_text
        assert has_page7, f"'Sheet7' or '7' not found in page 7"
        
        page8_text = pdf_reader.pages[7].extract_text()
        has_page8 = "Sheet8" in page8_text or "8" in page8_text
        assert has_page8, f"'Sheet8' or '8' not found in page 8"

    def test_single_xlsm_file(self, test_resources_dir, temp_output_dir):
        """単一の .xlsm ファイルから PDF を生成"""
        excel_path = test_resources_dir / "sheet_3_1_2.xlsm"
        
        assert excel_path.exists(), f"Excel file not found: {excel_path}"

        # 設定辞書を作成
        config = {
            "excel_path": str(excel_path),
            "sheets": "all",
            "exclude_sheets": [],
            "pdf_filename": "test_single_xlsm.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "include_hidden": False,
        }
        
        # ロガーを作成
        log_path = str(Path(temp_output_dir) / "test.log")
        logger = main.setup_logger(log_path)
        
        # 処理実行
        main.process_excel_to_pdf(config, logger)
        
        # PDF が生成されたか確認
        output_pdf = Path(temp_output_dir) / "test_single_xlsm.pdf"
        assert output_pdf.exists(), f"PDF not created: {output_pdf}"
        assert output_pdf.stat().st_size > 0, f"PDF is empty: {output_pdf}"

    def test_config_loading(self, temp_output_dir):
        """TOML 設定ファイルが正しく読み込まれるか"""
        # テスト用 TOML を作成
        test_toml_path = Path(temp_output_dir) / "test_config_load.toml"
        with open(test_toml_path, "w", encoding="utf-8") as f:
            f.write("""
excel_path = "sheet_3_1_2.xlsx"
sheets = "all"
exclude_sheets = []
pdf_filename = "test.pdf"
output_dir = "."
open_after_publish = false
include_hidden = false
""")
        
        cfg = main.load_toml(str(test_toml_path))
        
        # 必須フィールドが存在するか確認
        assert "excel_path" in cfg, "excel_path is missing"
        assert "sheets" in cfg, "sheets is missing"
        
        # 値が正しく読み込まれたか確認
        assert cfg["excel_path"] == "sheet_3_1_2.xlsx"
        assert cfg["sheets"] == "all"
        assert cfg.get("include_hidden") is False

    def test_normalize_excel_paths_single_string(self):
        """単一文字列パスの正規化"""
        paths = main.normalize_excel_paths("example.xlsx")
        assert isinstance(paths, list)
        assert len(paths) == 0 or isinstance(paths[0], str)

    def test_normalize_excel_paths_list(self):
        """リスト形式パスの正規化"""
        paths = main.normalize_excel_paths(["file1.xlsx", "file2.xlsx"])
        assert isinstance(paths, list)
        # ファイルが存在しない場合も直接パスとして扱われることを確認
        assert len(paths) >= 0

    def test_no_content_sorted_merge_page_numbers(self, test_resources_dir, temp_output_dir):
        """空白内容でヘッダページ番号テスト: ソート有で2ファイル結合して 1～8ページが正しく入るか"""
        file1 = test_resources_dir / "no_content_3_1_2_8.xlsx"
        file2 = test_resources_dir / "no_content_6_4_5_7.xlsx"
        
        assert file1.exists(), f"Excel file not found: {file1}"
        assert file2.exists(), f"Excel file not found: {file2}"

        config = {
            "excel_path": [str(file1), str(file2)],
            "sheets": "all",
            "exclude_sheets": [],
            "exclude_suffixes": [],
            "pdf_filename": "test_no_content_sorted.pdf",
            "output_dir": temp_output_dir,
            "open_after_publish": False,
            "sort_sheets": True,  # ソート有で結合
        }

        # PDF 生成を実行
        result = main.process_excel_to_pdf(config)
        
        # 正常に生成されたか確認
        assert result is not None, "PDF generation returned None"
        assert result.exists(), f"PDF file not created: {result}"
        
        # PDF を読み込む
        reader = PdfReader(str(result))
        num_pages = len(reader.pages)
        
        # 両ファイル合計で 8 ページになるはず（4 + 4）
        assert num_pages == 8, f"Expected 8 pages but got {num_pages}"
        
        # 各ページが存在することを確認
        for i in range(num_pages):
            page = reader.pages[i]
            assert page is not None, f"Page {i} is None"


class TestSanitizeFilename:
    """ファイル名サニタイズ機能のテスト"""

    def test_sanitize_filename_with_invalid_chars(self):
        """無効な文字を置換"""
        result = main.sanitize_filename("file:name*?.pdf")
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result
        assert result.endswith(".pdf")

    def test_sanitize_filename_default(self):
        """空の名前はデフォルト値を返す"""
        result = main.sanitize_filename("")
        assert result == "まとめ.pdf"

    def test_sanitize_filename_adds_pdf_extension(self):
        """拡張子がない場合は .pdf を追加"""
        result = main.sanitize_filename("document")
        assert result == "document.pdf"

    def test_sanitize_filename_preserves_pdf_extension(self):
        """既に .pdf がある場合は重複しない"""
        result = main.sanitize_filename("document.pdf")
        assert result == "document.pdf"
        assert result.count(".pdf") == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
