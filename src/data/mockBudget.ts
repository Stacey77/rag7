import type { BudgetData } from '../types/budget';

/** Sample budget data for demo/development. */
export const MOCK_BUDGET_DATA: BudgetData = {
  monthlyIncome: 5000,
  transactions: [
    { id: '1', date: new Date(Date.now() - 1 * 86400000).toISOString(), description: 'Grocery Store', amount: -120.5, category: 'Food' },
    { id: '2', date: new Date(Date.now() - 2 * 86400000).toISOString(), description: 'Gas Station', amount: -45.0, category: 'Transport' },
    { id: '3', date: new Date(Date.now() - 3 * 86400000).toISOString(), description: 'Netflix', amount: -15.99, category: 'Entertainment' },
    { id: '4', date: new Date(Date.now() - 4 * 86400000).toISOString(), description: 'Salary', amount: 2500.0, category: 'Income' },
    { id: '5', date: new Date(Date.now() - 5 * 86400000).toISOString(), description: 'Restaurant', amount: -62.0, category: 'Food' },
    { id: '6', date: new Date(Date.now() - 7 * 86400000).toISOString(), description: 'Pharmacy', amount: -28.5, category: 'Health' },
    { id: '7', date: new Date(Date.now() - 8 * 86400000).toISOString(), description: 'Amazon', amount: -89.99, category: 'Shopping' },
    { id: '8', date: new Date(Date.now() - 10 * 86400000).toISOString(), description: 'Gym Membership', amount: -40.0, category: 'Health' },
    { id: '9', date: new Date(Date.now() - 12 * 86400000).toISOString(), description: 'Coffee Shop', amount: -18.0, category: 'Food' },
    { id: '10', date: new Date(Date.now() - 14 * 86400000).toISOString(), description: 'Side Project Income', amount: 350.0, category: 'Income' },
    { id: '11', date: new Date(Date.now() - 15 * 86400000).toISOString(), description: 'Clothing Store', amount: -75.0, category: 'Shopping' },
    { id: '12', date: new Date(Date.now() - 16 * 86400000).toISOString(), description: 'Grocery Store', amount: -95.3, category: 'Food' },
    { id: '13', date: new Date(Date.now() - 18 * 86400000).toISOString(), description: 'Electric Bill', amount: -110.0, category: 'Utilities' },
    { id: '14', date: new Date(Date.now() - 20 * 86400000).toISOString(), description: 'Internet', amount: -59.99, category: 'Utilities' },
    { id: '15', date: new Date(Date.now() - 22 * 86400000).toISOString(), description: 'Paycheck', amount: 2500.0, category: 'Income' },
  ],
  bills: [
    {
      id: 'b1',
      name: 'Rent',
      amount: 1400,
      dueDate: new Date(Date.now() + 3 * 86400000).toISOString(),
      isPaid: false,
      isRecurring: true,
    },
    {
      id: 'b2',
      name: 'Car Insurance',
      amount: 145,
      dueDate: new Date(Date.now() + 6 * 86400000).toISOString(),
      isPaid: false,
      isRecurring: true,
    },
    {
      id: 'b3',
      name: 'Phone Bill',
      amount: 85,
      dueDate: new Date(Date.now() + 10 * 86400000).toISOString(),
      isPaid: false,
      isRecurring: true,
    },
    {
      id: 'b4',
      name: 'Streaming Services',
      amount: 45,
      dueDate: new Date(Date.now() - 2 * 86400000).toISOString(),
      isPaid: true,
      isRecurring: true,
    },
  ],
  goals: [
    {
      id: 'g1',
      name: 'Emergency Fund',
      targetAmount: 10000,
      currentAmount: 4200,
      targetDate: new Date(Date.now() + 365 * 86400000).toISOString(),
    },
    {
      id: 'g2',
      name: 'Vacation',
      targetAmount: 3000,
      currentAmount: 950,
      targetDate: new Date(Date.now() + 180 * 86400000).toISOString(),
    },
  ],
};
