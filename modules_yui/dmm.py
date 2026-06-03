"""
DMM (FANZA) アフィリエイト管理モジュール - 結衣専用
案件登録・クリック/成約記録・収益集計
"""

import uuid

from modules import ui
from . import storage


PRODUCTS_FILE     = "yui_dmm_products.json"
CONVERSIONS_FILE  = "yui_dmm_conversions.json"


def _load_products() -> list:
    return storage.load_list(PRODUCTS_FILE)


def _save_products(data: list):
    storage.save_list(PRODUCTS_FILE, data)


def _load_conversions() -> list:
    return storage.load_list(CONVERSIONS_FILE)


def _save_conversions(data: list):
    storage.save_list(CONVERSIONS_FILE, data)


def run():
    ui.header("DMM - アフィリエイト管理", ui.Color.YELLOW)

    while True:
        choice = ui.menu("DMMメニュー", [
            ("1", "案件を登録する"),
            ("2", "成約を記録する"),
            ("3", "案件一覧を表示"),
            ("4", "収益サマリー"),
            ("5", "案件別パフォーマンス"),
            ("0", "メインメニューに戻る"),
        ])

        if choice == "1":
            _register_product()
        elif choice == "2":
            _record_conversion()
        elif choice == "3":
            _show_products()
        elif choice == "4":
            _revenue_summary()
        elif choice == "5":
            _product_performance()
        elif choice == "0":
            break


def _register_product():
    ui.section("DMM案件を登録")

    name = ui.prompt("作品名・案件名")
    if not name:
        ui.error("案件名は必須です")
        return

    genre = ui.menu("ジャンル", [
        ("video",  "動画 (月額サービス・単品)"),
        ("goods",  "グッズ・書籍"),
        ("game",   "ゲーム"),
        ("other",  "その他"),
    ])

    link_type = ui.menu("リンクタイプ", [
        ("monthly", "月額サービス (継続課金)"),
        ("single",  "単品購入"),
        ("trial",   "無料体験誘導"),
    ])

    commission = ui.prompt_int("報酬単価 (円/件)", 500)
    aff_url    = ui.prompt("アフィリエイトURL")
    note       = ui.prompt("紹介文メモ (任意)")

    product = {
        "id":          str(uuid.uuid4())[:8],
        "name":        name,
        "genre":       genre,
        "link_type":   link_type,
        "commission":  commission or 0,
        "aff_url":     aff_url,
        "note":        note,
        "status":      "active",
        "created_at":  ui.now_str(),
    }

    products = _load_products()
    products.append(product)
    _save_products(products)

    ui.success(f"案件を登録しました (ID: {product['id']})")
    ui.info(f"  {name}  |  {commission}円/件  |  {link_type}")


def _record_conversion():
    ui.section("成約を記録")

    products = _load_products()
    if not products:
        ui.error("案件が登録されていません。先に案件を登録してください。")
        return

    ui.section("案件一覧")
    for p in products:
        print(f"  {ui.Color.CYAN}{p['id']}{ui.Color.RESET}  {p['name'][:30]}  ({p['commission']}円)")

    pid = ui.prompt("案件ID")
    product = next((p for p in products if p["id"] == pid), None)
    if not product:
        ui.error("IDが見つかりません")
        return

    date      = ui.prompt("成約日 (YYYY-MM-DD)", ui.today_str())
    count     = ui.prompt_int("成約数", 1)
    post_id   = ui.prompt("経由した投稿ID (任意)")
    clicks    = ui.prompt_int("リンククリック数 (任意)", 0)
    memo      = ui.prompt("メモ (任意)")

    revenue = (count or 1) * product["commission"]

    record = {
        "id":          str(uuid.uuid4())[:8],
        "product_id":  pid,
        "product_name": product["name"],
        "date":        date,
        "count":       count or 1,
        "clicks":      clicks or 0,
        "revenue":     revenue,
        "post_id":     post_id,
        "memo":        memo,
        "created_at":  ui.now_str(),
    }

    convs = _load_conversions()
    convs.append(record)
    _save_conversions(convs)

    ui.success(f"成約を記録しました")
    ui.info(f"  {product['name']}  x{count}件  =  {revenue:,}円")


def _show_products():
    products = _load_products()
    if not products:
        ui.info("案件が登録されていません")
        return

    convs = _load_conversions()
    ui.section("DMM案件一覧")
    rows = []
    for p in products:
        conv_total = sum(c["count"] for c in convs if c["product_id"] == p["id"])
        revenue    = sum(c["revenue"] for c in convs if c["product_id"] == p["id"])
        rows.append([
            p["id"],
            p["name"][:22],
            p["genre"],
            f"{p['commission']}円",
            f"{conv_total}件",
            f"{revenue:,}円",
            p["status"],
        ])
    ui.table(
        ["ID", "案件名", "ジャンル", "単価", "成約数", "収益", "状態"],
        rows,
        [10, 24, 8, 8, 7, 10, 8],
    )


def _revenue_summary():
    convs = _load_conversions()
    if not convs:
        ui.info("成約記録がありません")
        return

    ui.section("収益サマリー")

    total_conv    = sum(c["count"] for c in convs)
    total_revenue = sum(c["revenue"] for c in convs)
    total_clicks  = sum(c.get("clicks", 0) for c in convs)

    print(f"\n  {ui.Color.BOLD}総成約数  : {total_conv} 件{ui.Color.RESET}")
    print(f"  {ui.Color.BOLD}総収益    : {total_revenue:,} 円{ui.Color.RESET}")
    if total_clicks:
        ctr = round(total_conv / total_clicks * 100, 2)
        print(f"  総クリック: {total_clicks:,} 回 (成約率 {ctr}%)")

    # 月別集計
    monthly: dict[str, dict] = {}
    for c in convs:
        month = c["date"][:7]
        if month not in monthly:
            monthly[month] = {"conv": 0, "revenue": 0}
        monthly[month]["conv"]    += c["count"]
        monthly[month]["revenue"] += c["revenue"]

    if monthly:
        ui.section("月別収益")
        for month in sorted(monthly.keys()):
            m = monthly[month]
            bar = "█" * min(m["conv"], 20)
            print(f"  {month}  {bar:<20}  {m['conv']}件  {m['revenue']:,}円")


def _product_performance():
    products = _load_products()
    convs    = _load_conversions()

    if not products or not convs:
        ui.info("データが不足しています")
        return

    ui.section("案件別パフォーマンス (成約数順)")

    perf = []
    for p in products:
        p_convs   = [c for c in convs if c["product_id"] == p["id"]]
        conv_cnt  = sum(c["count"] for c in p_convs)
        revenue   = sum(c["revenue"] for c in p_convs)
        clicks    = sum(c.get("clicks", 0) for c in p_convs)
        conv_rate = round(conv_cnt / clicks * 100, 1) if clicks else 0.0
        perf.append((p["name"][:24], conv_cnt, revenue, clicks, conv_rate))

    perf.sort(key=lambda x: -x[1])

    rows = [[n, cnt, f"{rev:,}円", clk, f"{cr}%"] for n, cnt, rev, clk, cr in perf]
    ui.table(
        ["案件名", "成約数", "収益", "クリック", "成約率"],
        rows,
        [26, 7, 12, 9, 8],
    )
