import pandas as pd
import numpy as np
import quantstats_lumi.stats as stats

def test_sharpe_typical():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.sharpe(returns, periods=252)
    assert isinstance(val, float)

def test_sharpe_all_zeros():
    idx = pd.date_range('2020-01-01', periods=10, freq='D')
    returns = pd.Series(0.0, index=idx)
    val = stats.sharpe(returns)
    assert np.isnan(val) or val == 0.0

def test_sharpe_single_value():
    idx = pd.to_datetime(['2020-01-01'])
    returns = pd.Series([0.01], index=idx)
    val = stats.sharpe(returns)
    assert np.isnan(val)

def test_max_drawdown_simple():
    returns = pd.Series([0.1, -0.05, 0.02, -0.1, 0.03], index=pd.date_range('20200101', periods=5))
    val = stats.max_drawdown(returns)
    assert val < 0

def test_max_drawdown_all_positive():
    returns = pd.Series([0.01, 0.02, 0.005], index=pd.date_range('20200101', periods=3))
    val = stats.max_drawdown(returns)
    assert np.isclose(val, 0.0, atol=1e-6)

def test_volatility_annualized():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.volatility(returns, periods=252, annualize=True)
    assert val > 0

def test_volatility_all_zeros():
    idx = pd.date_range('2020-01-01', periods=10, freq='D')
    returns = pd.Series(0.0, index=idx)
    val = stats.volatility(returns)
    assert np.isclose(val, 0.0)

def test_sortino_typical():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.sortino(returns, periods=252)
    assert isinstance(val, float)

def test_calmar_typical():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.calmar(returns, periods=252)
    assert isinstance(val, float)

def test_profit_factor_positive():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=pd.date_range('2020-01-01', periods=5))
    val = stats.profit_factor(returns)
    assert val > 0

def test_payoff_ratio_typical():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=pd.date_range('2020-01-01', periods=5))
    val = stats.payoff_ratio(returns)
    assert val > 0

def test_risk_of_ruin_typical():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=pd.date_range('2020-01-01', periods=5))
    val = stats.risk_of_ruin(returns)
    assert 0 <= val <= 1

def test_kelly_criterion_typical():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=pd.date_range('2020-01-01', periods=5))
    val = stats.kelly_criterion(returns)
    assert isinstance(val, float)

def test_tail_ratio_typical():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02], index=pd.date_range('2020-01-01', periods=5))
    val = stats.tail_ratio(returns)
    assert val > 0

def test_information_ratio_typical():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    benchmark = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.information_ratio(returns, benchmark)
    assert isinstance(val, float)

def test_r_squared_typical():
    idx = pd.date_range('2020-01-01', periods=252, freq='B')
    returns = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    benchmark = pd.Series(np.random.normal(0.001, 0.01, len(idx)), index=idx)
    val = stats.r_squared(returns, benchmark)
    assert 0 <= val <= 1
