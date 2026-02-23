// Core data types for the budgeting app

export interface Transaction {
  id: string;
  date: string; // ISO date string
  description: string;
  amount: number; // negative = expense, positive = income
  category: string;
}

export interface Bill {
  id: string;
  name: string;
  amount: number;
  dueDate: string; // ISO date string
  isPaid: boolean;
  isRecurring: boolean;
}

export interface Goal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  targetDate: string;
}

export interface BudgetData {
  transactions: Transaction[];
  bills: Bill[];
  goals: Goal[];
  monthlyIncome: number;
}

export interface LocalInsights {
  topCategories: Array<{ category: string; total: number }>;
  largestExpense: Transaction | null;
  billsDueSoon: Bill[];
  savingsRate: number; // 0-1
  totalSpentThisMonth: number;
  totalIncomeThisMonth: number;
}
