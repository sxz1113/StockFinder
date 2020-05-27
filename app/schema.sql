DROP TABLE IF EXISTS fund_holding;
DROP TABLE IF EXISTS activity_history;

CREATE TABLE fund_holding (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Symbol TEXT NOT NULL,
  Stock TEXT NOT NULL,
  Fund TEXT NOT NULL,
  FundName TEXT not NULL,
  PortfolioPct REAL,
  Shares INTEGER,
  RecentActivity TEXT,
  ReportedPrice REAL,
  Value REAL
);

CREATE TABLE activity_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  Symbol TEXT NOT NULL,
  Fund TEXT NOT NULL,
  FundName TEXT not NULL,
  Period TEXT,
  Shares INTEGER,
  PortfolioPct REAL,
  Activity TEXT,
  PortfolioChange REAL,
  ReportedPrice REAL,
  FOREIGN KEY (Symbol) REFERENCES fund_holding (Symbol),
  FOREIGN KEY (Fund) REFERENCES fund_holding (Fund)
);

.mode csv
.import 'C:\Users\xxs85\Documents\Projects\Stocks\app\f13_fund_holding.csv' fund_holding
.import 'C:\Users\xxs85\Documents\Projects\Stocks\app\f13_activity_history.csv' activity_history
