from datetime import datetime
from sqlalchemy.orm import Session

from db.models import (
    Trade,
    Session as TradeSession,
    Expense,
    Payout,
    Evaluation,
    FundedAccount,
)


def _trade_pnl(trade: Trade) -> float:
    pnl = (trade.exit_price - trade.entry_price) * trade.quantity - trade.fees_commissions
    if trade.position_type and trade.position_type.lower() == "short":
        pnl = -pnl
    return pnl


def trade_metrics(trades: list[Trade]) -> dict[str, float]:
    if not trades:
        return {
            "pnl": 0.0,
            "win_rate": 0.0,
            "expectancy": 0.0,
            "drawdown": 0.0,
            "profit_factor": 0.0,
        }

    pnls = [_trade_pnl(trade) for trade in trades]
    total_pnl = sum(pnls)

    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]

    win_rate = len(wins) / len(pnls) if pnls else 0.0
    avg_profit = sum(wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0

    if losses:
        profit_factor = sum(wins) / abs(sum(losses)) if wins else 0.0
    else:
        profit_factor = float("inf") if wins else 0.0

    expectancy = (win_rate * avg_profit) - ((1 - win_rate) * avg_loss)

    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for pnl in pnls:
        cumulative += pnl
        if cumulative > peak:
            peak = cumulative
        drawdown = peak - cumulative
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return {
        "pnl": total_pnl,
        "win_rate": win_rate,
        "expectancy": expectancy,
        "drawdown": max_drawdown,
        "profit_factor": profit_factor,
    }


def lifetime_financials(session: Session) -> dict[str, float]:
    total_expenses = sum(expense.amount for expense in session.query(Expense).all())
    total_payouts = sum(payout.amount_net for payout in session.query(Payout).all())

    net_profit = total_payouts - total_expenses
    roi = total_payouts / total_expenses if total_expenses else 0.0

    return {
        "total_expenses": total_expenses,
        "total_payouts": total_payouts,
        "net_profit": net_profit,
        "roi": roi,
    }


def pass_rates(session: Session) -> dict[str, float]:
    evaluations = session.query(Evaluation).all()
    bought = len(evaluations)
    passed = sum(1 for evaluation in evaluations if evaluation.status == "passed")

    pass_rate = passed / bought if bought else 0.0

    total_funding = sum(
        account.account_size
        for account in session.query(FundedAccount).all()
        if account.status == "active"
    )

    return {"pass_rate": pass_rate, "total_funding": total_funding}
