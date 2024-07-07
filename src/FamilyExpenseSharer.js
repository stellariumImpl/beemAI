import React, { useState, useEffect } from 'react';
import './App.css';

function FamilyExpenseSharer() {
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [payer, setPayer] = useState('');
  const [message, setMessage] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [rejectedPayers, setRejectedPayers] = useState([]);
  const [analysis, setAnalysis] = useState('');
  const [currentSuggestedPayer, setCurrentSuggestedPayer] = useState('');
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setMessage('');
    setReason('');
    setRejectedPayers([]);
    setCurrentSuggestedPayer('');
    setShowConfirmation(false);

    try {
      const response = await fetch('http://localhost:5000/api/add_expense', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ amount: parseFloat(amount), category, payer, rejected_payers: rejectedPayers }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setReason(data.reason || '');
        if (!data.confirmed) {
          setCurrentSuggestedPayer(data.payer || '');
          setShowConfirmation(true);
        } else {
          setShowConfirmation(false);
        }
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('Failed to submit expense');
    } finally {
      setIsLoading(false);
    }

    if (!payer) {
      setAmount('');
      setCategory('');
    }
    setPayer('');
  };

  const confirmPayment = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/api/confirm_payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ payer: currentSuggestedPayer }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setShowConfirmation(false);
        setRejectedPayers([]);
        setCurrentSuggestedPayer('');
        analyzeExpenses();
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('Failed to confirm payment');
    } finally {
      setIsLoading(false);
    }
  };

  const rejectPayment = async () => {
    setIsLoading(true);
    setError('');
    setRejectedPayers([...rejectedPayers, currentSuggestedPayer]);

    try {
      const response = await fetch('http://localhost:5000/api/reject_payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payer: currentSuggestedPayer,
          category: category,
          amount: amount,
          rejected_payers: [...rejectedPayers, currentSuggestedPayer]
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setReason(data.reason || '');
        if (!data.confirmed) {
          setCurrentSuggestedPayer(data.payer || '');
          setShowConfirmation(true);
        } else {
          setShowConfirmation(false);
        }
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('Failed to reject payment');
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeExpenses = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5000/api/analyze_expenses');
      const data = await response.json();

      if (response.ok) {
        setAnalysis(data.analysis);
      } else {
        setError(data.error || 'An error occurred during analysis');
      }
    } catch (error) {
      setError('Failed to analyze expenses');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    analyzeExpenses();
  }, []);

  return (
    <div className="FamilyExpenseSharer">
      <h1>Family Expense Sharer</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Amount"
          required
        />
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          placeholder="Category"
          required
        />
        <input
          type="text"
          value={payer}
          onChange={(e) => setPayer(e.target.value)}
          placeholder="Payer (optional)"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Adding...' : 'Add Expense'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {message && (
        <div>
          <p>{message}</p>
          {reason && <p><strong>Reason:</strong> {reason}</p>}
          {showConfirmation && (
            <div>
              <p>Suggested payer: {currentSuggestedPayer}</p>
              <button onClick={confirmPayment} disabled={isLoading}>
                Accept Payment
              </button>
              <button onClick={rejectPayment} disabled={isLoading}>
                Reject Payment
              </button>
            </div>
          )}
        </div>
      )}
      <button onClick={analyzeExpenses} disabled={isLoading}>
        Analyze Expenses
      </button>
      {analysis && (
        <div className="analysis">
          <h2>Expense Analysis</h2>
          <pre>{analysis}</pre>
        </div>
      )}
    </div>
  );
}

export default FamilyExpenseSharer;