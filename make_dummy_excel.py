from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.title = "ランサーズ"
ws.append(["取得日時","タイトル","カテゴリ","価格","締切","URL","優先度スコア","スキル概要"])
wb.save("案件情報.xlsx")
print("OK: 案件情報.xlsx を作成しました")
