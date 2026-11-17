import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle, ArrowRight, CalendarDays, Check, CheckCircle2,
  ChevronRight, ClipboardList, Clock3, Layers3, Loader2, RotateCw,
  Sparkles, Target, Waypoints,
} from 'lucide-react';
import api from '../services/api';

const features = [
  { id: 'quiz', label: 'Quiz', icon: ClipboardList },
  { id: 'flashcards', label: 'Flashcards', icon: Layers3 },
  { id: 'mindmap', label: 'Mind map', icon: Waypoints },
  { id: 'planner', label: 'Study plan', icon: CalendarDays },
  { id: 'analytics', label: 'Progress', icon: Target },
];

function Panel({ children, className = '' }) {
  return <section className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</section>;
}

function DocumentSelect({ documents, value, onChange }) {
  return (
    <label className="flex min-w-0 flex-col gap-1 text-xs font-medium text-slate-500">
      Source document
      <select value={value} onChange={(event) => onChange(event.target.value)} className="min-w-[220px] rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
        <option value="">Select a PDF</option>
        {documents.map((document) => <option value={document.id} key={document.id}>{document.filename}</option>)}
      </select>
    </label>
  );
}

function SourceList({ sources }) {
  if (!sources?.length) return null;
  return (
    <details className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs">
      <summary className="cursor-pointer font-semibold text-slate-700">Grounded in {sources.length} source passages</summary>
      <div className="mt-3 space-y-2">
        {sources.map((source, index) => (
          <a
            key={`${source.chunk_id}-${index}`}
            href={api.getDocumentFileUrl(source.doc_id || '', source.page)}
            target="_blank"
            rel="noreferrer"
            className="block rounded-lg border border-slate-200 bg-white p-3 hover:border-blue-300"
          >
            <span className="font-semibold text-blue-700">{source.filename} · Page {source.page}</span>
            <p className="mt-1 whitespace-pre-wrap text-slate-600">{source.snippet}</p>
          </a>
        ))}
      </div>
    </details>
  );
}

export default function LearningPage({ feature, onNavigate, documents }) {
  const [docId, setDocId] = useState(documents[0]?.id || '');
  const [loading, setLoading] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [error, setError] = useState('');
  const [difficulty, setDifficulty] = useState('Medium');
  const [quizCount, setQuizCount] = useState(5);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [cards, setCards] = useState([]);
  const [cardIndex, setCardIndex] = useState(0);
  const [cardFlipped, setCardFlipped] = useState(false);
  const [mapData, setMapData] = useState(null);
  const [expandedBranch, setExpandedBranch] = useState(null);
  const [goal, setGoal] = useState('');
  const [plan, setPlan] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    if (!docId && documents.length) setDocId(documents[0].id);
  }, [documents, docId]);

  useEffect(() => {
    setError('');
    setQuiz(null);
    setQuizResult(null);
    setMapData(null);
    if (feature === 'flashcards') {
      api.getFlashcards(docId || null)
        .then((result) => { setCards(result.flashcards || []); setCardIndex(0); setCardFlipped(false); })
        .catch((err) => setError(err.response?.data?.detail || 'Could not load saved flashcards.'));
    }
    if (feature === 'planner') {
      api.getPlan()
        .then((savedPlan) => { setPlan(savedPlan); if (savedPlan?.goal) setGoal(savedPlan.goal); })
        .catch((err) => setError(err.response?.data?.detail || 'Could not load your study plan.'));
    }
    if (feature === 'analytics') {
      setAnalyticsLoading(true);
      api.getAnalytics()
        .then(setAnalytics)
        .catch((err) => setError(err.response?.data?.detail || 'Could not load learning analytics.'))
        .finally(() => setAnalyticsLoading(false));
    }
  }, [feature, docId]);

  const activeDocument = useMemo(() => documents.find((document) => document.id === docId), [documents, docId]);
  const run = async (action) => {
    if (!docId) {
      setError('Upload and select a PDF before generating study content.');
      return null;
    }
    setLoading(true);
    setError('');
    try {
      return await action();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'The study request failed. Please try again.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async () => {
    const result = await run(() => api.generateQuiz(docId, difficulty, Number(quizCount)));
    if (result) {
      setQuiz(result);
      setAnswers({});
      setQuizResult(null);
    }
  };

  const finishQuiz = async () => {
    if (!quiz) return;
    const result = await run(() => api.submitQuiz(quiz.id, answers));
    if (result) setQuizResult(result);
  };

  const generateCards = async () => {
    const result = await run(() => api.generateFlashcards(docId, 8));
    if (result) {
      setCards((current) => [...result.flashcards, ...current]);
      setCardIndex(0);
      setCardFlipped(false);
    }
  };

  const rateCard = async (rating) => {
    const card = cards[cardIndex];
    if (!card) return;
    try {
      await api.rateFlashcard(card.id, rating);
      setCards((current) => current.map((item) => item.id === card.id ? { ...item, rating } : item));
      setCardFlipped(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save your flashcard rating.');
    }
  };

  const generateMap = async () => {
    const result = await run(() => api.generateMindmap(docId));
    if (result) setMapData(result);
  };

  const generatePlan = async (event) => {
    event.preventDefault();
    const result = await run(() => api.generatePlan(docId, goal.trim()));
    if (result) setPlan(result);
  };

  const toggleTopic = async (topic) => {
    try {
      const updated = await api.updatePlanTopic(topic.id, !topic.completed);
      setPlan((current) => ({ ...current, topics: current.topics.map((item) => item.id === updated.id ? updated : item) }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update topic progress.');
    }
  };

  const heading = {
    quiz: 'Practice what you learned',
    flashcards: 'Review at your own pace',
    mindmap: 'See how concepts connect',
    planner: 'Turn your goal into a plan',
    analytics: 'Your learning at a glance',
  }[feature];

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">Study workspace</p>
          <h2 className="mt-1 text-2xl font-bold text-slate-800">{heading}</h2>
          <p className="mt-1 text-sm text-slate-500">Generated from the indexed content of your study PDFs.</p>
        </div>
        {feature !== 'analytics' && (
          <DocumentSelect documents={documents} value={docId} onChange={setDocId} />
        )}
      </div>

      <nav className="flex gap-2 overflow-x-auto rounded-xl border border-slate-200 bg-white p-2" aria-label="Study features">
        {features.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => onNavigate(id)} className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium ${feature === id ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}>
            <Icon className="h-4 w-4" /> {label}
          </button>
        ))}
      </nav>

      {error && <div role="alert" className="flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800"><AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />{error}</div>}
      {documents.length === 0 && feature !== 'analytics' && (
        <Panel><p className="text-sm text-slate-600">Upload a PDF in Study Materials to generate document-grounded learning tools.</p></Panel>
      )}

      {feature === 'quiz' && (
        <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
          <Panel className="h-fit space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800"><Sparkles className="h-4 w-4 text-indigo-600" /> Quiz settings</div>
            <label className="block text-xs font-medium text-slate-500">Difficulty
              <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                <option>Easy</option><option>Medium</option><option>Hard</option>
              </select>
            </label>
            <label className="block text-xs font-medium text-slate-500">Questions
              <select value={quizCount} onChange={(event) => setQuizCount(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                {[3, 5, 8, 10].map((number) => <option key={number} value={number}>{number} questions</option>)}
              </select>
            </label>
            <button onClick={startQuiz} disabled={loading || !documents.length} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardList className="h-4 w-4" />} Generate quiz
            </button>
            {activeDocument && <p className="text-xs text-slate-500">Questions will use {activeDocument.filename}.</p>}
          </Panel>
          <div className="space-y-4">
            {!quiz && <Panel className="flex min-h-64 flex-col items-center justify-center text-center"><ClipboardList className="h-9 w-9 text-indigo-300" /><p className="mt-3 text-sm font-semibold text-slate-700">Your quiz will appear here</p><p className="mt-1 text-xs text-slate-500">Each question is generated from retrieved PDF passages.</p></Panel>}
            {quiz && quizResult && (
              <Panel className="border-emerald-200 bg-emerald-50/50">
                <div className="flex items-center gap-3"><CheckCircle2 className="h-8 w-8 text-emerald-600" /><div><p className="font-bold text-slate-800">Quiz complete · {quizResult.score}/{quizResult.total}</p><p className="text-sm text-slate-600">{Math.round(quizResult.score / quizResult.total * 100)}% correct</p></div></div>
              </Panel>
            )}
            {quiz?.questions.map((question, index) => {
              const review = quizResult?.review[index];
              return (
                <Panel key={`${quiz.id}-${index}`} className="space-y-3">
                  <div className="flex items-start justify-between gap-3"><h3 className="text-sm font-semibold text-slate-800">{index + 1}. {question.question}</h3><span className="shrink-0 rounded-full bg-indigo-50 px-2 py-1 text-[10px] font-semibold text-indigo-700">{question.topic}</span></div>
                  <div className="grid gap-2">
                    {question.options.map((option, optionIndex) => {
                      const chosen = Number(answers[index]) === optionIndex;
                      const correct = review?.correct_index === optionIndex;
                      return (
                        <button
                          key={optionIndex}
                          type="button"
                          disabled={Boolean(quizResult)}
                          onClick={() => setAnswers((current) => ({ ...current, [index]: optionIndex }))}
                          className={`flex items-center gap-3 rounded-lg border p-3 text-left text-sm ${correct ? 'border-emerald-400 bg-emerald-50 text-emerald-900' : chosen ? 'border-indigo-400 bg-indigo-50 text-indigo-900' : 'border-slate-200 text-slate-700 hover:border-indigo-200'}`}
                        >
                          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-semibold">{String.fromCharCode(65 + optionIndex)}</span>{option}
                        </button>
                      );
                    })}
                  </div>
                  {review && <p className={`rounded-lg p-3 text-xs leading-relaxed ${review.correct ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-900'}`}><strong>{review.correct ? 'Correct.' : 'Review:'}</strong> {review.explanation}</p>}
                </Panel>
              );
            })}
            {quiz && !quizResult && <button onClick={finishQuiz} disabled={loading} className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50">{loading && <Loader2 className="h-4 w-4 animate-spin" />} Submit answers</button>}
            {quiz && <SourceList sources={quiz.sources} />}
          </div>
        </div>
      )}

      {feature === 'flashcards' && (
        <div className="grid gap-5 lg:grid-cols-[1fr_280px]">
          <Panel className="flex min-h-[420px] flex-col items-center justify-center">
            {cards.length === 0 ? (
              <div className="text-center"><Layers3 className="mx-auto h-10 w-10 text-indigo-300" /><p className="mt-3 text-sm font-semibold text-slate-700">No saved flashcards yet</p><p className="mt-1 text-xs text-slate-500">Generate a set from your selected PDF and they will be saved here.</p></div>
            ) : (
              <div className="w-full max-w-xl">
                <p className="mb-3 text-center text-xs text-slate-500">Card {cardIndex + 1} of {cards.length} · {cards[cardIndex]?.topic}</p>
                <button onClick={() => setCardFlipped((current) => !current)} className={`flip-card ${cardFlipped ? 'is-flipped' : ''}`} aria-label="Flip flashcard">
                  <span className="flip-card-inner">
                    <span className="flip-card-face"><span className="text-[10px] font-bold uppercase tracking-widest text-indigo-500">Question · click to flip</span><span className="mt-4 text-xl font-semibold text-slate-800">{cards[cardIndex]?.question}</span></span>
                    <span className="flip-card-face flip-card-back"><span className="text-[10px] font-bold uppercase tracking-widest text-emerald-600">Answer</span><span className="mt-4 text-base leading-relaxed text-slate-800">{cards[cardIndex]?.answer}</span></span>
                  </span>
                </button>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {['Easy', 'Medium', 'Hard'].map((rating) => <button key={rating} onClick={() => rateCard(rating)} className="rounded-full border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700">Mark {rating}</button>)}
                </div>
                <div className="mt-4 flex items-center justify-center gap-3">
                  <button disabled={cardIndex === 0} onClick={() => { setCardIndex((current) => current - 1); setCardFlipped(false); }} className="rounded-lg border border-slate-200 px-3 py-2 text-xs disabled:opacity-40">Previous</button>
                  <button disabled={cardIndex >= cards.length - 1} onClick={() => { setCardIndex((current) => current + 1); setCardFlipped(false); }} className="rounded-lg bg-indigo-600 px-3 py-2 text-xs font-medium text-white disabled:opacity-40">Next card <ChevronRight className="inline h-3 w-3" /></button>
                </div>
                {cards[cardIndex]?.source && <a href={api.getDocumentFileUrl(cards[cardIndex].doc_id || docId, cards[cardIndex].source.page)} target="_blank" rel="noreferrer" title={cards[cardIndex].source.snippet} className="mt-3 block text-center text-xs text-blue-700 hover:underline">Source: {cards[cardIndex].source.filename}, page {cards[cardIndex].source.page}</a>}
              </div>
            )}
          </Panel>
          <Panel className="h-fit space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800"><Sparkles className="h-4 w-4 text-indigo-600" /> Smart review</div>
            <p className="text-xs leading-relaxed text-slate-500">Create eight flashcards grounded in the selected document. Your ratings are saved for revision.</p>
            <button onClick={generateCards} disabled={loading || !documents.length} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />} Generate and save</button>
            <p className="text-xs text-slate-500">{cards.length} saved cards</p>
          </Panel>
        </div>
      )}

      {feature === 'mindmap' && (
        <Panel>
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div><h3 className="font-semibold text-slate-800">Concept map</h3><p className="mt-1 text-xs text-slate-500">Select a branch to expand its supporting subtopics.</p></div>
            <button onClick={generateMap} disabled={loading || !documents.length} className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Waypoints className="h-4 w-4" />} Generate mind map</button>
          </div>
          {!mapData && <div className="flex min-h-56 flex-col items-center justify-center text-center"><Waypoints className="h-10 w-10 text-indigo-300" /><p className="mt-3 text-sm text-slate-600">Generate a mind map to explore document topics and relationships.</p></div>}
          {mapData && (
            <div className="mindmap-canvas overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-5 md:p-8">
              <div className="mx-auto mb-8 max-w-sm rounded-2xl bg-indigo-600 px-5 py-4 text-center text-sm font-bold text-white shadow-lg">{mapData.topic}</div>
              <div className="mindmap-branches">
                {mapData.branches.map((branch, index) => (
                  <div key={`${branch.name}-${index}`} className="mindmap-branch">
                    <div className="mb-2 text-center text-[10px] font-medium text-slate-500">{branch.relationship || 'related to'}</div>
                    <button onClick={() => setExpandedBranch(expandedBranch === index ? null : index)} className={`w-full rounded-xl border p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${expandedBranch === index ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200 bg-white'}`}>
                      <span className="font-semibold text-slate-800">{branch.name}</span>
                      <span className="mt-1 block text-xs text-slate-500">{branch.children.length} subtopics · click to {expandedBranch === index ? 'collapse' : 'expand'}</span>
                    </button>
                    {expandedBranch === index && branch.children.length > 0 && <div className="mt-2 space-y-2 border-l-2 border-indigo-200 pl-3">{branch.children.map((child, childIndex) => <div key={`${child}-${childIndex}`} className="rounded-lg border border-indigo-100 bg-white px-3 py-2 text-xs text-slate-700"><ArrowRight className="mr-1 inline h-3 w-3 text-indigo-500" />{child}</div>)}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
          {mapData && <SourceList sources={mapData.sources} />}
        </Panel>
      )}

      {feature === 'planner' && (
        <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
          <Panel className="h-fit">
            <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-800"><Target className="h-4 w-4 text-indigo-600" /> Set your study goal</div>
            <form onSubmit={generatePlan} className="space-y-3">
              <label className="block text-xs font-medium text-slate-500">Goal
                <textarea value={goal} onChange={(event) => setGoal(event.target.value)} required maxLength={300} rows={4} placeholder="e.g. Review all machine learning topics before Friday's exam" className="mt-1 w-full rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-700" />
              </label>
              <button disabled={loading || !documents.length || !goal.trim()} className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CalendarDays className="h-4 w-4" />} Generate study plan</button>
            </form>
            {plan && <div className="mt-4 rounded-lg bg-indigo-50 p-3"><p className="text-xs font-semibold text-indigo-800">Current goal</p><p className="mt-1 text-sm text-slate-700">{plan.goal}</p></div>}
          </Panel>
          <Panel>
            <h3 className="font-semibold text-slate-800">Revision schedule</h3>
            {!plan && <p className="mt-4 text-sm text-slate-500">Your AI-generated plan will appear here.</p>}
            {plan?.topics?.length > 0 && <div className="mt-4 space-y-3">{plan.topics.map((topic) => (
              <label key={topic.id} className={`flex cursor-pointer items-start gap-3 rounded-xl border p-4 ${topic.completed ? 'border-emerald-200 bg-emerald-50/60' : 'border-slate-200'}`}>
                <input type="checkbox" checked={topic.completed} onChange={() => toggleTopic(topic)} className="mt-1 h-4 w-4 accent-emerald-600" />
                <span className="min-w-0 flex-1"><span className={`font-semibold ${topic.completed ? 'text-emerald-800 line-through' : 'text-slate-800'}`}>{topic.title}</span><span className="mt-1 block text-xs text-slate-500">{topic.day} · {topic.duration_minutes} min · {topic.reason}</span></span>
                {topic.completed && <Check className="h-4 w-4 text-emerald-600" />}
              </label>
            ))}</div>}
            {plan?.sources && <SourceList sources={plan.sources} />}
          </Panel>
        </div>
      )}

      {feature === 'analytics' && (
        <div className="space-y-5">
          {analyticsLoading && <Panel><div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-5 w-5 animate-spin text-indigo-600" />Loading your learning history…</div></Panel>}
          {analytics && (
            <>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {[
                  ['Completed quizzes', analytics.completed_quizzes, ClipboardList],
                  ['Average quiz score', `${analytics.average_score}%`, Target],
                  ['Study time', `${Math.floor(analytics.study_time_seconds / 3600)}h ${Math.floor((analytics.study_time_seconds % 3600) / 60)}m`, Clock3],
                  ['Saved flashcards', analytics.flashcards_saved, Layers3],
                ].map(([label, value, Icon]) => <Panel key={label} className="flex items-center gap-3"><span className="rounded-xl bg-indigo-50 p-3"><Icon className="h-5 w-5 text-indigo-600" /></span><span><span className="block text-xl font-bold text-slate-800">{value}</span><span className="text-xs text-slate-500">{label}</span></span></Panel>)}
              </div>
              <div className="grid gap-5 lg:grid-cols-2">
                <Panel>
                  <h3 className="font-semibold text-slate-800">Quiz score history</h3>
                  {!analytics.quiz_attempts.length && <p className="mt-4 text-sm text-slate-500">Complete a quiz to see your progress chart.</p>}
                  <div className="mt-4 space-y-3">
                    {analytics.quiz_attempts.slice(0, 8).map((attempt, index) => {
                      const score = Math.round(attempt.score / attempt.total * 100);
                      return <div key={attempt.id}><div className="mb-1 flex justify-between text-xs text-slate-600"><span>Attempt {analytics.quiz_attempts.length - index} · {attempt.difficulty}</span><span>{score}%</span></div><div className="h-2.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-500" style={{ width: `${score}%` }} /></div></div>;
                    })}
                  </div>
                </Panel>
                <Panel>
                  <div className="flex items-center justify-between"><h3 className="font-semibold text-slate-800">Study plan progress</h3><span className="text-sm font-bold text-indigo-600">{analytics.learning_progress}%</span></div>
                  <div className="mt-3 h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${analytics.learning_progress}%` }} /></div>
                  <p className="mt-2 text-xs text-slate-500">{analytics.topics_completed} of {analytics.topics_total} topics completed across saved plans.</p>
                  <h4 className="mt-6 text-sm font-semibold text-slate-800">Topics to revisit</h4>
                  {!analytics.weak_topics.length && <p className="mt-2 text-xs text-slate-500">No weak topics identified yet. Complete quizzes to get recommendations.</p>}
                  <div className="mt-2 space-y-2">{analytics.weak_topics.map((item) => <div key={item.topic} className="flex items-center justify-between rounded-lg bg-amber-50 px-3 py-2 text-xs"><span className="font-medium text-slate-700">{item.topic}</span><span className="font-semibold text-amber-800">{item.accuracy}% · {item.attempted} questions</span></div>)}</div>
                </Panel>
              </div>
              <Panel><h3 className="font-semibold text-slate-800">Completed quizzes</h3><div className="mt-3 divide-y divide-slate-100">{analytics.quiz_attempts.map((attempt) => <div key={attempt.id} className="flex items-center justify-between gap-3 py-3 text-sm"><span className="text-slate-700">{attempt.difficulty} quiz · {new Date(attempt.completed_at).toLocaleDateString()}</span><span className="font-semibold text-slate-800">{attempt.score}/{attempt.total}</span></div>)}</div></Panel>
            </>
          )}
        </div>
      )}
    </div>
  );
}
