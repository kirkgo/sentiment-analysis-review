import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, Loader2 } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

const COLORS = ['#10B981', '#3B82F6', '#EF4444']
const SENTIMENT_COLORS = {
  Positive: '#10B981',
  Neutral: '#3B82F6',
  Negative: '#EF4444'
}

export default function SentimentDashboard() {
  const [stats, setStats] = useState(null)
  const [text, setText] = useState('')
  const [sentiment, setSentiment] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/sentiment-stats')
      const data = await response.json()
      setStats(data)
    } catch (err) {
      setError('Failed to fetch sentiment statistics')
    }
  }

  const updateLocalStats = (newSentiment) => {
    setStats(prevStats => {
      const updatedStats = { ...prevStats }
      updatedStats[newSentiment] += 1
      return updatedStats
    })
  }

  const updateServerStats = async (newSentiment) => {
    try {
      const response = await fetch('http://localhost:8000/update-stats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sentiment: newSentiment }),
      })
      if (!response.ok) {
        throw new Error('Failed to update server statistics')
      }
    } catch (err) {
      console.error('Error updating server statistics:', err)
      setError('Failed to update server statistics')
    }
  }

  const analyzeSentiment = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze')
      return
    }
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/analyze-sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      const data = await response.json()
      setSentiment(data.sentiment)
      updateLocalStats(data.sentiment)
      await updateServerStats(data.sentiment)
      setError(null)
    } catch (err) {
      setError('Failed to analyze sentiment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center text-gray-800">Sentiment Analysis Dashboard</h1>
        <p className="text-center text-gray-600">Analyze product reviews and gain insights into overall customer sentiment.</p>
        
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {stats && (
          <Card>
            <CardHeader>
              <CardTitle>Overall Sentiment Statistics</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col md:flex-row justify-around items-center space-y-8 md:space-y-0">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={Object.entries(stats).map(([name, value]) => ({ name, value }))}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {Object.entries(stats).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={Object.entries(stats).map(([name, value]) => ({ name, value }))}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8">
                    {Object.entries(stats).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Analyze New Text</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter product review text..."
              rows={4}
            />
            <Button 
              onClick={analyzeSentiment} 
              disabled={loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing
                </>
              ) : (
                'Analyze'
              )}
            </Button>
          </CardContent>
        </Card>
        
        {sentiment && (
          <Card>
            <CardHeader>
              <CardTitle>Analysis Result</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg">
                Sentiment: <span className="font-bold" style={{color: SENTIMENT_COLORS[sentiment]}}>{sentiment}</span>
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
