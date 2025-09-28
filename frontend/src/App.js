import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const ExerciseCard = ({ exercise, onSelect }) => {
  const getYouTubeVideoId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    return match ? match[1] : null;
  };

  const videoId = getYouTubeVideoId(exercise.video_url);
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

  const getTypeColor = (type) => {
    switch (type) {
      case 'abdominal': return 'bg-gradient-to-r from-blue-500 to-blue-600';
      case 'pectoral': return 'bg-gradient-to-r from-purple-500 to-purple-600';
      case 'cardio': return 'bg-gradient-to-r from-red-500 to-red-600';
      case 'full_body': return 'bg-gradient-to-r from-green-500 to-green-600';
      default: return 'bg-gradient-to-r from-gray-500 to-gray-600';
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'beginner': return 'text-green-400';
      case 'intermediate': return 'text-yellow-400';
      case 'advanced': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden shadow-2xl hover:shadow-primary/20 transition-all duration-300 hover:scale-105 cursor-pointer"
         onClick={() => onSelect(exercise)}>
      <div className="relative">
        <img 
          src={thumbnailUrl} 
          alt={exercise.name}
          className="w-full h-48 object-cover"
        />
        <div className={`absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-semibold text-white ${getTypeColor(exercise.exercise_type)}`}>
          {exercise.exercise_type.toUpperCase()}
        </div>
        <div className="absolute top-3 right-3 bg-black/70 px-2 py-1 rounded-full">
          <span className={`text-xs font-semibold ${getLevelColor(exercise.level)}`}>
            {exercise.level.toUpperCase()}
          </span>
        </div>
      </div>
      
      <div className="p-5">
        <h3 className="text-xl font-bold text-white mb-2">{exercise.name}</h3>
        <p className="text-gray-300 text-sm mb-4 line-clamp-2">{exercise.description}</p>
        
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-4 text-sm text-gray-400">
            <span>⏱️ {exercise.default_duration}s</span>
            {exercise.default_repetitions && (
              <span>🔄 {exercise.default_repetitions} reps</span>
            )}
          </div>
        </div>
        
        <div className="flex flex-wrap gap-1">
          {exercise.muscle_groups.slice(0, 3).map((muscle, index) => (
            <span key={index} className="bg-primary/20 text-primary text-xs px-2 py-1 rounded-full">
              {muscle}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

const ExerciseModal = ({ exercise, isOpen, onClose, onStartWorkout }) => {
  if (!isOpen || !exercise) return null;

  const getYouTubeVideoId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    return match ? match[1] : null;
  };

  const videoId = getYouTubeVideoId(exercise.video_url);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">{exercise.name}</h2>
              <p className="text-gray-300">{exercise.description}</p>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white text-2xl p-2"
            >
              ✕
            </button>
          </div>

          {/* Video */}
          <div className="mb-6 rounded-xl overflow-hidden">
            <iframe
              width="100%"
              height="315"
              src={`https://www.youtube.com/embed/${videoId}`}
              title={exercise.name}
              frameBorder="0"
              allowFullScreen
              className="rounded-xl"
            ></iframe>
          </div>

          {/* Exercise Details */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-xl font-semibold text-white mb-3">Detalles del Ejercicio</h3>
              <div className="space-y-2 text-gray-300">
                <div className="flex justify-between">
                  <span>Duración:</span>
                  <span className="text-primary font-semibold">{exercise.default_duration}s</span>
                </div>
                <div className="flex justify-between">
                  <span>Descanso:</span>
                  <span className="text-primary font-semibold">{exercise.default_rest}s</span>
                </div>
                {exercise.default_repetitions && (
                  <div className="flex justify-between">
                    <span>Repeticiones:</span>
                    <span className="text-primary font-semibold">{exercise.default_repetitions}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Nivel:</span>
                  <span className="text-primary font-semibold capitalize">{exercise.level}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-3">Músculos Trabajados</h3>
              <div className="flex flex-wrap gap-2">
                {exercise.muscle_groups.map((muscle, index) => (
                  <span key={index} className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
                    {muscle}
                  </span>
                ))}
              </div>
              
              {exercise.equipment.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-white font-semibold mb-2">Equipamiento:</h4>
                  <div className="flex flex-wrap gap-2">
                    {exercise.equipment.map((item, index) => (
                      <span key={index} className="bg-secondary/20 text-secondary px-3 py-1 rounded-full text-sm">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Instructions */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-white mb-3">Instrucciones</h3>
            <ol className="space-y-2">
              {exercise.instructions.map((instruction, index) => (
                <li key={index} className="text-gray-300 flex items-start">
                  <span className="bg-primary text-black rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-1 flex-shrink-0">
                    {index + 1}
                  </span>
                  {instruction}
                </li>
              ))}
            </ol>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => onStartWorkout(exercise)}
              className="flex-1 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary text-black font-bold py-3 px-6 rounded-xl transition-all duration-300 transform hover:scale-105"
            >
              🏃‍♂️ Comenzar Ejercicio
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-600 text-gray-300 hover:text-white hover:border-gray-400 rounded-xl transition-all duration-300"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const Timer = ({ exercise, onComplete, onStop }) => {
  const [timeLeft, setTimeLeft] = useState(exercise.default_duration);
  const [isResting, setIsResting] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [currentSet, setCurrentSet] = useState(1);
  const [totalSets] = useState(3); // Default to 3 sets

  useEffect(() => {
    let interval = null;
    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      if (!isResting) {
        // Work phase completed, start rest
        setIsResting(true);
        setTimeLeft(exercise.default_rest);
      } else {
        // Rest phase completed
        if (currentSet < totalSets) {
          // Start next set
          setCurrentSet(currentSet + 1);
          setIsResting(false);
          setTimeLeft(exercise.default_duration);
        } else {
          // Workout completed
          onComplete({
            exercise_id: exercise.id,
            sets_completed: totalSets,
            total_duration: (exercise.default_duration + exercise.default_rest) * totalSets
          });
        }
      }
    }
    return () => clearInterval(interval);
  }, [isRunning, timeLeft, isResting, currentSet, totalSets, exercise, onComplete]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);
  };

  const resetTimer = () => {
    setIsRunning(false);
    setTimeLeft(exercise.default_duration);
    setIsResting(false);
    setCurrentSet(1);
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-8 text-center max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-white mb-2">{exercise.name}</h2>
      <div className="text-sm text-gray-400 mb-6">
        Serie {currentSet} de {totalSets}
      </div>
      
      <div className="mb-8">
        <div className={`text-6xl font-bold mb-2 ${isResting ? 'text-yellow-400' : 'text-primary'}`}>
          {formatTime(timeLeft)}
        </div>
        <div className={`text-lg font-semibold ${isResting ? 'text-yellow-400' : 'text-primary'}`}>
          {isResting ? '🛌 DESCANSO' : '🏃‍♂️ EJERCICIO'}
        </div>
      </div>

      <div className="flex gap-4 justify-center">
        <button
          onClick={toggleTimer}
          className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 ${
            isRunning 
              ? 'bg-yellow-500 hover:bg-yellow-400 text-black' 
              : 'bg-green-500 hover:bg-green-400 text-black'
          }`}
        >
          {isRunning ? '⏸️ Pausar' : '▶️ Iniciar'}
        </button>
        
        <button
          onClick={resetTimer}
          className="px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white rounded-xl font-bold transition-all duration-300"
        >
          🔄 Reiniciar
        </button>
        
        <button
          onClick={onStop}
          className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold transition-all duration-300"
        >
          ⏹️ Parar
        </button>
      </div>
    </div>
  );
};

const App = () => {
  const [exercises, setExercises] = useState([]);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [activeTimer, setActiveTimer] = useState(null);
  const [workoutStats, setWorkoutStats] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExercises();
    fetchWorkoutStats();
  }, []);

  const fetchExercises = async () => {
    try {
      const response = await axios.get(`${API}/exercises`);
      setExercises(response.data);
    } catch (error) {
      console.error('Error fetching exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkoutStats = async () => {
    try {
      const response = await axios.get(`${API}/workouts/stats`);
      setWorkoutStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleExerciseSelect = (exercise) => {
    setSelectedExercise(exercise);
    setShowModal(true);
  };

  const handleStartWorkout = (exercise) => {
    setShowModal(false);
    setActiveTimer(exercise);
  };

  const handleWorkoutComplete = async (workoutData) => {
    try {
      const sessionData = {
        date: new Date().toISOString().split('T')[0],
        exercises_completed: [workoutData],
        total_duration: workoutData.total_duration,
        difficulty_rating: null,
        energy_level: null,
        notes: null
      };
      
      await axios.post(`${API}/workouts`, sessionData);
      setActiveTimer(null);
      fetchWorkoutStats();
      
      // Show completion message
      alert('¡Felicidades! Has completado el ejercicio. 🎉');
    } catch (error) {
      console.error('Error saving workout:', error);
    }
  };

  const handleStopWorkout = () => {
    setActiveTimer(null);
  };

  const filteredExercises = exercises.filter(exercise => 
    filterType === 'all' || exercise.exercise_type === filterType
  );

  const exerciseTypes = [
    { value: 'all', label: 'Todos', icon: '🎯' },
    { value: 'abdominal', label: 'Abdominal', icon: '💪' },
    { value: 'pectoral', label: 'Pectoral', icon: '🏋️' },
    { value: 'cardio', label: 'Cardio', icon: '❤️' },
    { value: 'full_body', label: 'Cuerpo Completo', icon: '🏃' }
  ];

  if (activeTimer) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center p-4">
        <Timer 
          exercise={activeTimer} 
          onComplete={handleWorkoutComplete}
          onStop={handleStopWorkout}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      {/* Header */}
      <header className="bg-black/50 backdrop-blur-lg border-b border-gray-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                💪 FitnessApp
              </h1>
              <p className="text-gray-400 mt-1">Tu rutina personalizada de fitness</p>
            </div>
            
            {workoutStats && (
              <div className="hidden md:flex space-x-6 text-center">
                <div>
                  <div className="text-2xl font-bold text-primary">{workoutStats.total_sessions}</div>
                  <div className="text-xs text-gray-400">Sesiones</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-primary">{Math.round(workoutStats.total_workout_time / 60)}m</div>
                  <div className="text-xs text-gray-400">Tiempo Total</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-primary">{workoutStats.recent_sessions}</div>
                  <div className="text-xs text-gray-400">Este Mes</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Filter Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-2 mb-8">
          {exerciseTypes.map(type => (
            <button
              key={type.value}
              onClick={() => setFilterType(type.value)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${
                filterType === type.value
                  ? 'bg-primary text-black'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {type.icon} {type.label}
            </button>
          ))}
        </div>

        {/* Exercises Grid */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-primary text-xl">Cargando ejercicios...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredExercises.map(exercise => (
              <ExerciseCard 
                key={exercise.id} 
                exercise={exercise} 
                onSelect={handleExerciseSelect}
              />
            ))}
          </div>
        )}

        {filteredExercises.length === 0 && !loading && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏃‍♂️</div>
            <h3 className="text-xl text-gray-400 mb-2">No se encontraron ejercicios</h3>
            <p className="text-gray-500">Prueba con otro filtro</p>
          </div>
        )}
      </div>

      {/* Exercise Modal */}
      <ExerciseModal 
        exercise={selectedExercise}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onStartWorkout={handleStartWorkout}
      />
    </div>
  );
};

export default App;
