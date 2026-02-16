import React, { useState, useMemo } from 'react';
import { Calculator, DollarSign, TrendingUp, Users, Clock, Zap, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import type { ROICalculation } from '../../types';

export const ROICalculator: React.FC = () => {
  const [inputs, setInputs] = useState({
    currentMonthlyCost: 50000,
    teamSize: 15,
    avgHourlyRate: 75,
    manualHoursPerMonth: 320,
    errorRate: 5,
    processingTimeHours: 160
  });

  const calculation = useMemo((): ROICalculation & { 
    errorReduction: number;
    timeReduction: number;
    productivityGain: number;
    monthlyErrorCost: number;
    monthlyTimeSavings: number;
  } => {
    // AI platform cost (tiered pricing)
    const aiMonthlyCost = inputs.teamSize <= 10 ? 5000 : 
                          inputs.teamSize <= 25 ? 8000 : 
                          inputs.teamSize <= 50 ? 12000 : 18000;

    // Calculate savings
    const manualLaborCost = inputs.manualHoursPerMonth * inputs.avgHourlyRate;
    const errorCostReduction = (inputs.currentMonthlyCost * inputs.errorRate / 100) * 0.8; // 80% error reduction
    const timeEfficiency = inputs.processingTimeHours * inputs.avgHourlyRate * 0.6; // 60% time savings
    
    const monthlySavings = manualLaborCost * 0.7 + errorCostReduction + timeEfficiency - aiMonthlyCost;
    const annualSavings = monthlySavings * 12;
    
    // Productivity metrics
    const productivityGain = ((manualLaborCost * 0.7 + timeEfficiency) / inputs.currentMonthlyCost) * 100;
    
    // Break-even calculation (months)
    const implementationCost = 25000; // One-time setup
    const breakEven = monthlySavings > 0 ? implementationCost / monthlySavings : 0;

    return {
      currentCost: inputs.currentMonthlyCost,
      aiCost: aiMonthlyCost,
      monthlySavings: Math.max(0, monthlySavings),
      annualSavings: Math.max(0, annualSavings),
      productivity: productivityGain,
      breakEven: breakEven,
      errorReduction: 80,
      timeReduction: 60,
      productivityGain: productivityGain,
      monthlyErrorCost: errorCostReduction,
      monthlyTimeSavings: timeEfficiency
    };
  }, [inputs]);

  const projectionData = Array.from({ length: 12 }, (_, i) => ({
    month: `Month ${i + 1}`,
    manual: inputs.currentMonthlyCost,
    withAI: calculation.aiCost,
    savings: calculation.monthlySavings
  }));

  const cumulativeSavings = Array.from({ length: 12 }, (_, i) => ({
    month: `M${i + 1}`,
    savings: calculation.monthlySavings * (i + 1) - (i === 0 ? 25000 : 0)
  }));

  const handleInputChange = (field: keyof typeof inputs, value: number) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">ROI Calculator</h1>
          <p className="text-gray-400">Calculate your return on investment with AI automation</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">Reset</button>
          <button className="btn-primary">Save Report</button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Monthly Savings</div>
          <div className="text-3xl font-bold text-green-400">
            ${calculation.monthlySavings.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">After AI implementation</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Annual Savings</div>
          <div className="text-3xl font-bold gradient-text">
            ${calculation.annualSavings.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">First year projection</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Break-even Point</div>
          <div className="text-3xl font-bold text-blue-400">
            {calculation.breakEven.toFixed(1)}
          </div>
          <div className="text-xs text-gray-500 mt-1">Months to ROI</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Productivity Gain</div>
          <div className="text-3xl font-bold text-purple-400">
            +{calculation.productivity.toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Efficiency improvement</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Parameters */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <Calculator className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold">Input Parameters</h2>
          </div>

          <div className="space-y-6">
            {/* Current Monthly Cost */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <DollarSign className="w-4 h-4" />
                Current Monthly Operating Cost
              </label>
              <input
                type="number"
                value={inputs.currentMonthlyCost}
                onChange={(e) => handleInputChange('currentMonthlyCost', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            {/* Team Size */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <Users className="w-4 h-4" />
                Team Size
              </label>
              <input
                type="number"
                value={inputs.teamSize}
                onChange={(e) => handleInputChange('teamSize', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            {/* Average Hourly Rate */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <DollarSign className="w-4 h-4" />
                Average Hourly Rate ($)
              </label>
              <input
                type="number"
                value={inputs.avgHourlyRate}
                onChange={(e) => handleInputChange('avgHourlyRate', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            {/* Manual Hours */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <Clock className="w-4 h-4" />
                Manual Processing Hours/Month
              </label>
              <input
                type="number"
                value={inputs.manualHoursPerMonth}
                onChange={(e) => handleInputChange('manualHoursPerMonth', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            {/* Error Rate */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <TrendingUp className="w-4 h-4" />
                Current Error Rate (%)
              </label>
              <input
                type="number"
                value={inputs.errorRate}
                onChange={(e) => handleInputChange('errorRate', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            {/* Processing Time */}
            <div>
              <label className="flex items-center gap-2 text-sm text-gray-400 mb-2">
                <Zap className="w-4 h-4" />
                Processing Time Hours/Month
              </label>
              <input
                type="number"
                value={inputs.processingTimeHours}
                onChange={(e) => handleInputChange('processingTimeHours', Number(e.target.value))}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Savings Breakdown */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-bold">Savings Breakdown</h2>
          </div>

          <div className="space-y-4 mb-6">
            <div className="p-4 rounded-lg bg-gradient-to-r from-green-500/10 to-transparent border border-green-500/20">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">Labor Cost Reduction</span>
                <span className="font-bold text-green-400">
                  ${(inputs.manualHoursPerMonth * inputs.avgHourlyRate * 0.7).toLocaleString()}
                </span>
              </div>
              <div className="text-xs text-gray-500">70% automation of manual tasks</div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-transparent border border-blue-500/20">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">Error Cost Reduction</span>
                <span className="font-bold text-blue-400">
                  ${calculation.monthlyErrorCost.toLocaleString()}
                </span>
              </div>
              <div className="text-xs text-gray-500">{calculation.errorReduction}% reduction in errors</div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-purple-500/10 to-transparent border border-purple-500/20">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">Time Efficiency Gains</span>
                <span className="font-bold text-purple-400">
                  ${calculation.monthlyTimeSavings.toLocaleString()}
                </span>
              </div>
              <div className="text-xs text-gray-500">{calculation.timeReduction}% faster processing</div>
            </div>

            <div className="p-4 rounded-lg bg-gradient-to-r from-orange-500/10 to-transparent border border-orange-500/20">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">AI Platform Cost</span>
                <span className="font-bold text-orange-400">
                  -${calculation.aiCost.toLocaleString()}
                </span>
              </div>
              <div className="text-xs text-gray-500">Monthly subscription</div>
            </div>
          </div>

          <div className="pt-4 border-t border-gray-700">
            <div className="flex justify-between items-center">
              <span className="text-lg font-bold">Net Monthly Savings</span>
              <span className="text-2xl font-bold gradient-text">
                ${calculation.monthlySavings.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Cost Comparison Chart */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Monthly Cost Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={projectionData.slice(0, 6)}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#F3F4F6' }}
            />
            <Legend />
            <Bar dataKey="manual" fill="#EF4444" name="Manual Process" />
            <Bar dataKey="withAI" fill="#8B5CF6" name="With AI" />
            <Bar dataKey="savings" fill="#10B981" name="Savings" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Cumulative Savings */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Cumulative Savings Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={cumulativeSavings}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#F3F4F6' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="savings" 
              stroke="#10B981" 
              strokeWidth={3}
              name="Cumulative Savings"
              dot={{ fill: '#10B981', r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Key Insights */}
      <div className="card">
        <h3 className="text-lg font-bold mb-4">Key Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
            <div className="font-semibold mb-2">💰 First Year ROI</div>
            <div className="text-sm text-gray-400">
              You'll save ${calculation.annualSavings.toLocaleString()} in the first year, 
              achieving break-even in just {calculation.breakEven.toFixed(1)} months.
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
            <div className="font-semibold mb-2">⚡ Productivity Boost</div>
            <div className="text-sm text-gray-400">
              Team productivity increases by {calculation.productivity.toFixed(0)}%, allowing focus on high-value strategic work.
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20">
            <div className="font-semibold mb-2">🎯 Error Reduction</div>
            <div className="text-sm text-gray-400">
              {calculation.errorReduction}% reduction in errors saves approximately ${calculation.monthlyErrorCost.toLocaleString()}/month in rework costs.
            </div>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20">
            <div className="font-semibold mb-2">⏱️ Time Savings</div>
            <div className="text-sm text-gray-400">
              {calculation.timeReduction}% faster processing frees up {(inputs.processingTimeHours * 0.6).toFixed(0)} hours per month for your team.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
