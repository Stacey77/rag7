'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Save, Send, ArrowLeft, ArrowRight } from 'lucide-react';
import type { InterviewResponse } from '@/types';

const interviewQuestions = [
  {
    category: 'Workflow Mapping',
    questions: [
      'Describe your typical daily workflow from start to finish.',
      'What are the main tasks you perform regularly?',
      'Which tasks consume the most time in your day?',
    ],
  },
  {
    category: 'Task Analysis',
    questions: [
      'Which tasks do you perform daily? Weekly? Monthly?',
      'Approximately how long does each major task take?',
      'Which tasks require the most manual effort?',
    ],
  },
  {
    category: 'Bottlenecks',
    questions: [
      'What are the biggest pain points in your current workflow?',
      'Where do you experience the most delays or friction?',
      'Which processes often require rework or corrections?',
    ],
  },
  {
    category: 'Data & Integration',
    questions: [
      'Do you manually enter data between different systems? Which ones?',
      'How much time do you spend on data entry tasks?',
      'Are there frequent copy-paste operations between tools?',
    ],
  },
  {
    category: 'Approvals & Handoffs',
    questions: [
      'Describe your approval processes. How long do they typically take?',
      'How many manual handoffs occur in your typical workflows?',
      'Which handoffs cause the most delays?',
    ],
  },
  {
    category: 'Error Correction',
    questions: [
      'What types of errors occur most frequently in your work?',
      'How much time do you spend correcting errors?',
      'What causes these errors (manual entry, miscommunication, etc.)?',
    ],
  },
];

export function Interview() {
  const [title, setTitle] = useState('');
  const [currentCategory, setCurrentCategory] = useState(0);
  const [responses, setResponses] = useState<InterviewResponse[]>([]);
  const [currentAnswers, setCurrentAnswers] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  const totalCategories = interviewQuestions.length;
  const progress = ((currentCategory + 1) / totalCategories) * 100;
  const currentSection = interviewQuestions[currentCategory];

  const handleAnswerChange = (questionIndex: number, answer: string) => {
    setCurrentAnswers({
      ...currentAnswers,
      [questionIndex]: answer,
    });
  };

  const handleNext = () => {
    // Save current answers
    const newResponses = currentSection.questions.map((question, index) => ({
      question,
      answer: currentAnswers[index] || '',
      category: currentSection.category,
    }));

    setResponses([
      ...responses.filter((r) => r.category !== currentSection.category),
      ...newResponses,
    ]);

    if (currentCategory < totalCategories - 1) {
      setCurrentCategory(currentCategory + 1);
      // Load existing answers for next category if any
      const existingAnswers: Record<string, string> = {};
      interviewQuestions[currentCategory + 1].questions.forEach((q, i) => {
        const existing = responses.find(
          (r) => r.question === q && r.category === interviewQuestions[currentCategory + 1].category
        );
        if (existing) {
          existingAnswers[i] = existing.answer;
        }
      });
      setCurrentAnswers(existingAnswers);
    }
  };

  const handlePrevious = () => {
    if (currentCategory > 0) {
      setCurrentCategory(currentCategory - 1);
      // Load existing answers
      const existingAnswers: Record<string, string> = {};
      interviewQuestions[currentCategory - 1].questions.forEach((q, i) => {
        const existing = responses.find(
          (r) => r.question === q && r.category === interviewQuestions[currentCategory - 1].category
        );
        if (existing) {
          existingAnswers[i] = existing.answer;
        }
      });
      setCurrentAnswers(existingAnswers);
    }
  };

  const handleSaveDraft = async () => {
    setIsSaving(true);
    try {
      // TODO: Implement API call to save draft
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert('Draft saved successfully!');
    } catch (error) {
      alert('Failed to save draft');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmit = async () => {
    // Save current answers first
    const newResponses = currentSection.questions.map((question, index) => ({
      question,
      answer: currentAnswers[index] || '',
      category: currentSection.category,
    }));

    const allResponses = [
      ...responses.filter((r) => r.category !== currentSection.category),
      ...newResponses,
    ];

    setIsSaving(true);
    try {
      // TODO: Implement API call to submit interview
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert('Interview submitted successfully! Redirecting to analysis...');
      // window.location.href = '/analysis';
    } catch (error) {
      alert('Failed to submit interview');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="container mx-auto max-w-4xl p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Workflow Interview</h1>
        <p className="text-muted-foreground">
          Help us understand your workflow to identify automation opportunities
        </p>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">
                Section {currentCategory + 1} of {totalCategories}
              </span>
              <span className="text-muted-foreground">{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} />
          </div>
        </CardContent>
      </Card>

      {/* Interview Title */}
      {currentCategory === 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Interview Title</CardTitle>
            <CardDescription>Give this interview a descriptive name</CardDescription>
          </CardHeader>
          <CardContent>
            <Input
              placeholder="e.g., Sales Department Workflow Analysis"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </CardContent>
        </Card>
      )}

      {/* Questions */}
      <Card>
        <CardHeader>
          <CardTitle>{currentSection.category}</CardTitle>
          <CardDescription>
            Answer the following questions about your workflow
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {currentSection.questions.map((question, index) => (
            <div key={index} className="space-y-2">
              <Label htmlFor={`q-${index}`} className="text-base">
                {index + 1}. {question}
              </Label>
              <Textarea
                id={`q-${index}`}
                placeholder="Your answer..."
                value={currentAnswers[index] || ''}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentCategory === 0}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Previous
        </Button>

        <Button variant="outline" onClick={handleSaveDraft} disabled={isSaving}>
          <Save className="mr-2 h-4 w-4" />
          Save Draft
        </Button>

        {currentCategory < totalCategories - 1 ? (
          <Button onClick={handleNext}>
            Next
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={isSaving}>
            <Send className="mr-2 h-4 w-4" />
            Submit Interview
          </Button>
        )}
      </div>
    </div>
  );
}
