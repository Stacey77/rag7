/**
 * Computes local, non-AI insights from budget data.
 * Used in fallback mode when AI is unavailable.
 */

import type { BudgetData, LocalInsights, Transaction } from '../types/budget';

export function computeLocalInsights(data: BudgetData): LocalInsights {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const sevenDaysFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

  const recentTransactions = data.transactions.filter(
    (t) => new Date(t.date) >= thirtyDaysAgo,
  );

  // Top spending categories
  const categoryTotals: Record<string, number> = {};
  recentTransactions
    .filter((t) => t.amount < 0)
    .forEach((t) => {
      categoryTotals[t.category] =
        (categoryTotals[t.category] ?? 0) + Math.abs(t.amount);
    });
  const topCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([category, total]) => ({ category, total }));

  // Largest single expense in last 30 days
  const expenses = recentTransactions.filter((t) => t.amount < 0);
  let largestExpense: Transaction | null = null;
  for (const t of expenses) {
    if (!largestExpense || Math.abs(t.amount) > Math.abs(largestExpense.amount)) {
      largestExpense = t;
    }
  }

  // Bills due in the next 7 days
  const billsDueSoon = data.bills.filter((b) => {
    if (b.isPaid) return false;
    const due = new Date(b.dueDate);
    return due >= now && due <= sevenDaysFromNow;
  });

  // Savings rate: (income - |expenses|) / income
  const totalIncomeThisMonth = recentTransactions
    .filter((t) => t.amount > 0)
    .reduce((s, t) => s + t.amount, 0);
  const totalSpentThisMonth = recentTransactions
    .filter((t) => t.amount < 0)
    .reduce((s, t) => s + Math.abs(t.amount), 0);
  const effectiveIncome = totalIncomeThisMonth || data.monthlyIncome;
  const savingsRate =
    effectiveIncome > 0
      ? Math.max(0, (effectiveIncome - totalSpentThisMonth) / effectiveIncome)
      : 0;

  return {
    topCategories,
    largestExpense,
    billsDueSoon,
    savingsRate,
    totalSpentThisMonth,
    totalIncomeThisMonth: effectiveIncome,
  };
}
