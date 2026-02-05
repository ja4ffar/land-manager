# -*- coding: utf-8 -*-

from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "land.db"

PAGE = """
<!doctype html>
<html lang="ar">
<head>
<meta charset="utf-8">
<title>إدارة بيع الأراضي</title>
<style>
body { font-family: Arial; direction: rtl; padding: 15px; }
table { border-collapse: collapse; width: 100%; margin-top: 10px; }
th, td { border: 1px solid #444; padding: 6px; text-align: center; }
th { background: #eee; }
input, select, button { padding: 5px; margin: 3px; }
</style>
</head>
<body>

<h2>إدارة بيع قطع الأراضي (نسخة ويب)</h2>

<form method="post" action="/add">
<input name="customer" placeholder="الاسم" required>
<input name="phone" placeholder="الهاتف">
<input name="plot_no" placeholder="رقم القطعة" required>

<select name="sale_type">
<option>نقد</option>
<option>دين</option>
<option>أقساط</option>
</select>

<input name="total" placeholder="السعر الكلي" required>
<input name="paid" placeholder="المدفوع" value="0">
<input name="note" placeholder="ملاحظة">

<button type="submit">إضافة</button>
</form>

<hr>

<form method="get">
<input name="search" placeholder="بحث بالاسم / الهاتف / القطعة">
<button type="submit">بحث</button>
<a href="/">إظهار الكل</a>
</form>

<table>
<tr>
<th>الاسم</th>
<th>الهاتف</th>
<th>القطعة</th>
<th>النوع</th>
<th>السعر</th>
<th>المدفوع</th>
<th>المتبقي</th>
<th>ملاحظة</th>
</tr>

{% for r in rows %}
<tr>
<td>{{ r[1] }}</td>
<td>{{ r[2] }}</td>
<td>{{ r[3] }}</td>
<td>{{ r[4] }}</td>
<td>{{ r[5] }}</td>
<td>{{ r[6] }}</td>
<td>{{ r[7] }}</td>
<td>{{ r[8] }}</td>
</tr>
{% endfor %}
</table>

<h3>مجموع الديون: {{ total_debt }}</h3>

</body>
</html>
"""

def get_rows(search=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if search:
        cur.execute("""
            SELECT * FROM sales
            WHERE customer LIKE ? OR phone LIKE ? OR plot_no LIKE ?
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM sales")

    rows = cur.fetchall()
    conn.close()
    return rows

@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search")
    rows = get_rows(search)
    total_debt = sum(r[7] for r in rows if r[7] > 0)
    return render_template_string(PAGE, rows=rows, total_debt=total_debt)

@app.route("/add", methods=["POST"])
def add():
    customer = request.form["customer"]
    phone = request.form["phone"]
    plot_no = request.form["plot_no"]
    sale_type = request.form["sale_type"]
    total = float(request.form["total"])
    paid = float(request.form["paid"] or 0)
    note = request.form["note"]
    remaining = total - paid

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sales
        (customer, phone, plot_no, sale_type, total, paid, remaining, note, date)
        VALUES (?,?,?,?,?,?,?,?,date('now'))
    """, (customer, phone, plot_no, sale_type, total, paid, remaining, note))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run()

