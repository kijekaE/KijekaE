import sqlite3
import shutil
import os

DB_PATH = '/Users/vrushank/Documents/Work/Pruthatek/Projects/KijekaE/db.sqlite3'

# Backup
bak = DB_PATH + '.bak'
if not os.path.exists(bak):
    shutil.copy2(DB_PATH, bak)
    print('Backup created at', bak)
else:
    print('Backup already exists at', bak)

html = '''<!DOCTYPE html>
<html lang=""en"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>Polypropylene Chemical Pump</title>
</head>
<body>

<h2 style=""color:#004A99;font-size:24px;font-weight:700;margin-top:30px;margin-bottom:15px;"">
    Features of Polypropylene Chemical Pump
</h2>

<p>&bull; Self-priming vertical lift pump Designed primarily for use with antifreeze, detergents etc.</p>
<p>&bull; Polypropylene construction with stainless steel plunger rod & Viton seals</p>
<p>&bull; Complete with 2"" polypropylene bung adaptor</p>
<p>&bull; Nylon Chemical Pumps. KE201NL</p>
<table style=""width:100%;border-collapse:collapse;margin-bottom:20px;"">
  <thead>
    <tr style=""background-color:#004A99;color:white;"">
      <th style=""border:1px solid #ddd;padding:10px;text-align:left;"">Pump Type</th>
      <th style=""border:1px solid #ddd;padding:10px;text-align:left;"">Vertical Lift Piston</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style=""border:1px solid #ddd;padding:10px;"">Pump Drive Type</td>
      <td style=""border:1px solid #ddd;padding:10px;"">Manual/Hand Operated</td>
    </tr>
    <tr>
      <td style=""border:1px solid #ddd;padding:10px;"">Flow Rate /Output</td>
      <td style=""border:1px solid #ddd;padding:10px;"">Up 40 ML / Stroke</td>
    </tr>
    <tr>
      <td style=""border:1px solid #ddd;padding:10px;"">Wetted Components</td>
      <td style=""border:1px solid #ddd;padding:10px;"">Polypropylene, Steel & Viton</td>
    </tr>
    <tr>
      <td style=""border:1px solid #ddd;padding:10px;"">For Use With</td>
      <td style=""border:1px solid #ddd;padding:10px;"">Antifreeze, detergents, windshield fluids, glycerine, mild acids, most petroleum based media etc.</td>
    </tr>
    <tr>
      <td style=""border:1px solid #ddd;padding:10px;"">Do Not Use With</td>
      <td style=""border:1px solid #ddd;padding:10px;"">With Strong acids, Lacquers, acetone, gasoline etc.</td>
    </tr>
  </tbody>
</table>
<p>&bull; For More Detail about Product Kindly email us on: info@kijeka.com</p>

<p>&bull; Polypropylene body resists most acids and alkalis</p>
<p>&bull; Manual or electric drive</p>
<p>&bull; Drum pump tube design for 200 L drums</p>
<p>&bull; Chemical-resistant seals</p>
<p>&bull; Multiple flow rate options</p>

<h2 style=""color:#004A99;font-size:24px;font-weight:700;margin-top:30px;margin-bottom:15px;"">
    Use Cases
</h2>

<p>&bull; Transferring acids and alkalis in chemical plants</p>
<p>&bull; Water treatment chemical dosing</p>
<p>&bull; Electroplating bath chemical circulation</p>
<p>&bull; Agricultural chemical application</p>

<h2 style=""color:#004A99;font-size:24px;font-weight:700;margin-top:30px;margin-bottom:15px;"">
    Industries Using Polypropylene Chemical Pump
</h2>

<p>&bull; Chemical</p>
<p>&bull; Water Treatment</p>
<p>&bull; Electroplating</p>
<p>&bull; Agriculture</p>
<p>&bull; Pharmaceuticals</p>

<h2 style=""color:#004A99;font-size:24px;font-weight:700;margin-top:30px;margin-bottom:15px;"">
    Safety Benefits
</h2>

<p>&bull; Enclosed wetted parts prevent chemical splash exposure</p>
<p>&bull; Drip-free design reduces floor contamination and slip hazard</p>
<p>&bull; Chemical-compatible materials prevent corrosion failure</p>
<p>&bull; Bonding/grounding options for flammable liquid pumping</p>

<h2 style=""color:#004A99;font-size:24px;font-weight:700;margin-top:30px;margin-bottom:15px;"">
    Frequently Asked Questions (FAQs)
</h2>

<h3 style=""color:#004A99;font-size:18px;font-weight:600;margin-top:20px;margin-bottom:10px;"">
    Q: What chemicals is PP compatible with?
</h3>
<p>
    A: Acids, alkalis, and most organic solvents; check chemical compatibility chart.
</p>

<h3 style=""color:#004A99;font-size:18px;font-weight:600;margin-top:20px;margin-bottom:10px;"">
    Q: What flow rate does it deliver?
</h3>
<p>
    A: Typically 40–80 L/min depending on model.
</p>

<h3 style=""color:#004A99;font-size:18px;font-weight:600;margin-top:20px;margin-bottom:10px;"">
    Q: Is it food-grade?
</h3>
<p>
    A: Food-grade PP versions available.
</p>

</body>
</html>'''

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Count matching rows
cur.execute("SELECT COUNT(*) FROM api_product WHERE id < ? AND productName = ?", (697, 'Polypropylene Chemical Pump'))
match_count = cur.fetchone()[0]
print('Matching rows found:', match_count)

if match_count == 0:
    print('No rows to update. Exiting.')
else:
    cur.execute("UPDATE api_product SET description = ? WHERE id < ? AND productName = ?", (html, 697, 'Polypropylene Chemical Pump'))
    conn.commit()
    print('Update committed.')
    cur.execute("SELECT id FROM api_product WHERE id < ? AND productName = ?", (697, 'Polypropylene Chemical Pump'))
    ids = [r[0] for r in cur.fetchall()]
    print('Updated IDs:', ids)

conn.close()
