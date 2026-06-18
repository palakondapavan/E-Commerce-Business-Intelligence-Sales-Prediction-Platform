# Power BI Dashboard — Setup Guide & DAX Reference
## E-Commerce Business Intelligence Platform

---

## 1. Data Source Configuration

### Import the Cleaned Dataset
1. Open **Power BI Desktop**
2. Click **Get Data → Text/CSV**
3. Navigate to: `Dataset/Amazon_Sale_Report_Cleaned.csv`
4. Click **Transform Data**

### Data Types in Power Query
| Column | Type |
|---|---|
| date | Date |
| qty | Whole Number |
| amount | Decimal Number |
| unit_price | Decimal Number |
| year | Whole Number |
| month | Whole Number |
| ship_postal_code | Text |
| All others | Text |

---

## 2. Data Model

### Table: Amazon_Sales (Fact)
- Primary table from the cleaned CSV
- One row per order line

### Table: Date (Dimension — create in Power Query)
```m
let
    StartDate = #date(2022, 1, 1),
    EndDate   = #date(2022, 12, 31),
    NumDays   = Duration.Days(EndDate - StartDate) + 1,
    DateList  = List.Dates(StartDate, NumDays, #duration(1,0,0,0)),
    Table     = Table.FromList(DateList, Splitter.SplitByNothing(),
                               {"Date"}, null, ExtraValues.Error),
    AddYear   = Table.AddColumn(Table, "Year",    each Date.Year([Date]),   Int64.Type),
    AddMonth  = Table.AddColumn(AddYear,"Month",  each Date.Month([Date]),  Int64.Type),
    AddMonNm  = Table.AddColumn(AddMonth,"MonthName", each Date.ToText([Date],"MMM"), type text),
    AddQtr    = Table.AddColumn(AddMonNm,"Quarter",   each Date.QuarterOfYear([Date]), Int64.Type),
    AddWk     = Table.AddColumn(AddQtr, "WeekNum",  each Date.WeekOfYear([Date]),    Int64.Type),
    AddDay    = Table.AddColumn(AddWk,  "DayName",  each Date.DayOfWeekName([Date]), type text)
in AddDay
```
Mark this table as a **Date Table** (Table Tools → Mark as Date Table → Date).

### Relationships
```
Date[Date]        → Amazon_Sales[date]    (1:Many, Single Filter Direction)
```

---

## 3. DAX Measures — KPIs

```dax
-- ══════════════════════════════════════════
--  CORE KPI MEASURES
-- ══════════════════════════════════════════

Total Revenue =
    SUMX(
        FILTER(Amazon_Sales, Amazon_Sales[status] <> "Cancelled"),
        Amazon_Sales[amount]
    )

Total Orders =
    DISTINCTCOUNT(Amazon_Sales[order_id])

Total Quantity Sold =
    SUM(Amazon_Sales[qty])

Avg Order Value =
    DIVIDE([Total Revenue], [Total Orders], 0)

-- ══════════════════════════════════════════
--  STATUS KPIs
-- ══════════════════════════════════════════

Delivered Orders =
    CALCULATE(
        DISTINCTCOUNT(Amazon_Sales[order_id]),
        FILTER(Amazon_Sales,
               Amazon_Sales[status] = "Delivered" ||
               Amazon_Sales[status] = "Shipped - Delivered To Buyer")
    )

Cancelled Orders =
    CALCULATE(
        DISTINCTCOUNT(Amazon_Sales[order_id]),
        Amazon_Sales[status] = "Cancelled"
    )

Cancellation Rate % =
    DIVIDE([Cancelled Orders], [Total Orders], 0) * 100

Delivery Rate % =
    DIVIDE([Delivered Orders], [Total Orders], 0) * 100

-- ══════════════════════════════════════════
--  TIME INTELLIGENCE
-- ══════════════════════════════════════════

Revenue MoM Change =
    VAR CurrentMonth = [Total Revenue]
    VAR PrevMonth    = CALCULATE([Total Revenue],
                           DATEADD('Date'[Date], -1, MONTH))
    RETURN CurrentMonth - PrevMonth

Revenue MoM Growth % =
    DIVIDE([Revenue MoM Change],
           CALCULATE([Total Revenue], DATEADD('Date'[Date], -1, MONTH)),
           0) * 100

Revenue YTD =
    TOTALYTD([Total Revenue], 'Date'[Date])

Revenue PYTD =
    CALCULATE([Revenue YTD],
              SAMEPERIODLASTYEAR('Date'[Date]))

Revenue YoY % =
    DIVIDE([Revenue YTD] - [Revenue PYTD], [Revenue PYTD], 0) * 100

-- ══════════════════════════════════════════
--  CATEGORY & PRODUCT
-- ══════════════════════════════════════════

Category Revenue Share % =
    DIVIDE(
        CALCULATE([Total Revenue]),
        CALCULATE([Total Revenue], ALL(Amazon_Sales[category])),
        0
    ) * 100

Top Category =
    CALCULATE(
        FIRSTNONBLANK(Amazon_Sales[category], 1),
        TOPN(1,
             SUMMARIZE(Amazon_Sales, Amazon_Sales[category],
                       "Rev", [Total Revenue]),
             [Rev], DESC)
    )

-- ══════════════════════════════════════════
--  B2B METRICS
-- ══════════════════════════════════════════

B2B Revenue =
    CALCULATE([Total Revenue], Amazon_Sales[b2b] = "Yes")

B2C Revenue =
    CALCULATE([Total Revenue], Amazon_Sales[b2b] = "No")

B2B Revenue % =
    DIVIDE([B2B Revenue], [Total Revenue], 0) * 100

-- ══════════════════════════════════════════
--  PROMOTION IMPACT
-- ══════════════════════════════════════════

Promo Revenue =
    CALCULATE([Total Revenue],
              Amazon_Sales[promotion_ids] <> "No Promotion")

Non-Promo Revenue =
    CALCULATE([Total Revenue],
              Amazon_Sales[promotion_ids] = "No Promotion")

Promo Lift % =
    DIVIDE(
        CALCULATE([Avg Order Value], Amazon_Sales[promotion_ids] <> "No Promotion") -
        CALCULATE([Avg Order Value], Amazon_Sales[promotion_ids] = "No Promotion"),
        CALCULATE([Avg Order Value], Amazon_Sales[promotion_ids] = "No Promotion"),
        0
    ) * 100
```

---

## 4. Report Pages & Visual Specifications

### Page 1 — Executive Overview
| Visual | Type | X-Axis / Legend | Y-Axis / Values | Settings |
|---|---|---|---|---|
| Total Revenue | KPI Card | — | Total Revenue | Format: ₹#,##0.00 |
| Total Orders | KPI Card | — | Total Orders | Format: #,##0 |
| Total Qty Sold | KPI Card | — | Total Quantity Sold | Format: #,##0 |
| Avg Order Value | KPI Card | — | Avg Order Value | Format: ₹#,##0 |
| Revenue Trend | Line Chart | Date[MonthName] | Total Revenue | Markers On |
| Orders Trend | Clustered Bar | Date[MonthName] | Total Orders | Sort by Month |
| Status Donut | Donut Chart | status | Total Orders | Data labels: % |
| Top Categories | Bar Chart | category | Total Revenue | Top N = 10 |
| Top States | Map Visual | ship_state | Total Revenue | Bubble size |

### Page 2 — Product & Category Analysis
| Visual | Type | Fields |
|---|---|---|
| Category Matrix | Matrix | Rows: category / Cols: MonthName / Values: Total Revenue |
| Top SKUs | Table | sku, style, category, Total Revenue, Total Quantity Sold |
| Size Analysis | Treemap | Category: size / Values: Total Quantity Sold |
| Price Distribution | Histogram | unit_price (bins of 200) |

### Page 3 — Geographic Analysis
| Visual | Type | Fields |
|---|---|---|
| India Map | Filled Map | Location: ship_state / Color: Total Revenue |
| City Rankings | Bar Chart (horizontal) | ship_city / Total Orders (Top 15) |
| State × Category | Matrix | Rows: ship_state / Cols: category / Values: Revenue |

### Page 4 — Channel & Operations
| Visual | Type | Fields |
|---|---|---|
| Channel Revenue | Clustered Bar | sales_channel / Total Revenue |
| Fulfilment Split | Pie Chart | fulfilment / Total Orders |
| Service Level KPIs | KPI Card | ship_service_level / Avg Order Value |
| B2B vs B2C Trend | Line Chart | date / B2B Revenue & B2C Revenue |

---

## 5. Filters / Slicers (All Pages)

```
Slicer 1: Date Range     → Date[Date]   (Between)
Slicer 2: Category       → category     (Dropdown, Multi-Select)
Slicer 3: State          → ship_state   (Dropdown, Multi-Select)
Slicer 4: Status         → status       (List, Multi-Select)
Slicer 5: Sales Channel  → sales_channel (Toggle)
Slicer 6: B2B / B2C      → b2b           (Toggle)
```

---

## 6. Theme Configuration (JSON)

Save as `PowerBI/ecommerce_theme.json` and import via **View → Themes → Browse for Themes**:

```json
{
  "name": "ECommerce BI Dark",
  "dataColors": [
    "#00c8ff","#ff4d6d","#ffd166","#06d6a0",
    "#c77dff","#ff9f1c","#a8dadc","#f72585",
    "#4cc9f0","#b5e48c"
  ],
  "background": "#0d0d1a",
  "foreground": "#e8e8f0",
  "tableAccent": "#00c8ff",
  "visualStyles": {
    "*": {
      "*": {
        "background": [{"color": {"solid": {"color": "#13132b"}}}],
        "border":     [{"color": {"solid": {"color": "#1c1c3a"}}}]
      }
    },
    "card": {
      "*": {
        "calloutValue": [{"fontSize": 28, "fontBold": true}],
        "label":        [{"fontSize": 10, "fontColor": {"solid":{"color":"#aaaacc"}}}]
      }
    }
  }
}
```

---

## 7. Power BI Service Publishing Checklist

- [ ] Enable Row-Level Security if sharing with multiple regions
- [ ] Schedule data refresh (if connected to live database)
- [ ] Set up email subscriptions for weekly KPI snapshots
- [ ] Export to PDF for offline executive reports
- [ ] Publish to Workspace → Share Dashboard link
- [ ] Enable Q&A feature for natural language queries
- [ ] Configure mobile layout for Page 1 (Executive Overview)
