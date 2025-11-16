import React, { useState, useEffect } from 'react';
import { Plane, MapPin, DollarSign, Calendar, Star, Filter, LogOut, User, History } from 'lucide-react';

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change to your FastAPI server URL

// Utility function for API calls
const api = {
  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    return response.json();
  },
  
  async get(endpoint, token) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, { headers });
    if (!response.ok) throw new Error('API request failed');
    return response.json();
  }
};

// Main App Component
export default function TravelPlannerApp() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [currentView, setCurrentView] = useState('auth');
  const [authMode, setAuthMode] = useState('login');

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setCurrentView('main');
    }
  }, []);

  const handleLogin = async (credentials) => {
    try {
      const result = await api.post('/auth/login', credentials);
      setToken(result.token);
      setUser({ user_id: result.user_id, username: result.username });
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify({ user_id: result.user_id, username: result.username }));
      setCurrentView('main');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleSignup = async (credentials) => {
    try {
      const result = await api.post('/auth/signup', credentials);
      setToken(result.token);
      setUser({ user_id: result.user_id, username: result.username });
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify({ user_id: result.user_id, username: result.username }));
      setCurrentView('main');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleLogout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentView('auth');
  };

  if (currentView === 'auth') {
    return (
      <AuthView 
        mode={authMode} 
        setMode={setAuthMode}
        onLogin={handleLogin}
        onSignup={handleSignup}
      />
    );
  }

  return (
    <MainApp 
      user={user} 
      token={token}
      onLogout={handleLogout}
      currentView={currentView}
      setCurrentView={setCurrentView}
    />
  );
}

// Authentication View
function AuthView({ mode, setMode, onLogin, onSignup }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    city: '',
    country: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = mode === 'login' 
        ? await onLogin({ email: formData.email, password: formData.password })
        : await onSignup(formData);

      if (!result.success) {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <Plane className="w-16 h-16 mx-auto text-blue-600 mb-4" />
          <h1 className="text-3xl font-bold text-gray-800">Travel Planner</h1>
          <p className="text-gray-600 mt-2">Plan your perfect journey</p>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2 rounded-lg font-medium transition ${
              mode === 'login' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setMode('signup')}
            className={`flex-1 py-2 rounded-lg font-medium transition ${
              mode === 'signup' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          
          {mode === 'signup' && (
            <input
              type="text"
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          )}
          
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            minLength={6}
          />
          
          {mode === 'signup' && (
            <>
              <input
                type="text"
                placeholder="City"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <input
                type="text"
                placeholder="Country"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign Up'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Main Application
function MainApp({ user, token, onLogout, currentView, setCurrentView }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Plane className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-800">Travel Planner</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => setCurrentView('main')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentView === 'main' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Plan Trip
              </button>
              <button
                onClick={() => setCurrentView('trips')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentView === 'trips' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <History className="w-5 h-5 inline mr-1" />
                My Trips
              </button>
              <div className="flex items-center gap-2 text-gray-700">
                <User className="w-5 h-5" />
                <span className="font-medium">{user.username}</span>
              </div>
              <button
                onClick={onLogout}
                className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium transition"
              >
                <LogOut className="w-5 h-5 inline mr-1" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'main' && <PlanningView user={user} token={token} />}
        {currentView === 'trips' && <TripsView user={user} token={token} />}
      </div>
    </div>
  );
}

// Planning View
function PlanningView({ user, token }) {
  const [step, setStep] = useState('trip-details');
  const [tripData, setTripData] = useState({
    maxBudget: '',
    startDate: '',
    endDate: '',
    destinationCity: '',
    destinationCountry: ''
  });
  const [suggestions, setSuggestions] = useState([]);
  const [filteredDestinations, setFilteredDestinations] = useState([]);
  const [filters, setFilters] = useState({ budget: '', destination: '', category: '' });
  const [loading, setLoading] = useState(false);
  const [currentTrip, setCurrentTrip] = useState(null);

  const handleCreateTrip = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await api.post('/planning/create-trip', {
        user_id: user.user_id,
        max_budget: parseFloat(tripData.maxBudget),
        start_date: tripData.startDate,
        end_date: tripData.endDate,
        destination_city: tripData.destinationCity || null,
        destination_country: tripData.destinationCountry || null
      });
      setCurrentTrip(result.trip_id);
      setStep('suggestions');
    } catch (error) {
      alert('Error creating trip: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const result = await api.get(`/planning/suggestions/${user.user_id}`, token);
      setSuggestions(result.suggestions || []);
    } catch (error) {
      alert('Error fetching suggestions: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = async () => {
    setLoading(true);
    try {
      const result = await api.post('/planning/filter', {
        user_id: user.user_id,
        budget: filters.budget ? parseFloat(filters.budget) : null,
        destination: filters.destination || null,
        category: filters.category || null
      });
      setFilteredDestinations(result.destinations || []);
      setStep('filtered');
    } catch (error) {
      alert('Error applying filters: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (step === 'trip-details') {
    return (
      <div className="max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Plan Your Trip</h2>
        <form onSubmit={handleCreateTrip} className="bg-white rounded-xl shadow-lg p-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Budget ($)
            </label>
            <input
              type="number"
              value={tripData.maxBudget}
              onChange={(e) => setTripData({ ...tripData, maxBudget: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
              min="0"
              step="0.01"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={tripData.startDate}
                onChange={(e) => setTripData({ ...tripData, startDate: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={tripData.endDate}
                onChange={(e) => setTripData({ ...tripData, endDate: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred City (Optional)
            </label>
            <input
              type="text"
              value={tripData.destinationCity}
              onChange={(e) => setTripData({ ...tripData, destinationCity: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Paris"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Country (Optional)
            </label>
            <input
              type="text"
              value={tripData.destinationCountry}
              onChange={(e) => setTripData({ ...tripData, destinationCountry: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., France"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Continue to Suggestions'}
          </button>
        </form>
      </div>
    );
  }

  if (step === 'suggestions') {
    return (
      <div>
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Discover Destinations</h2>
        
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <button
            onClick={fetchSuggestions}
            disabled={loading}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Show Random Suggestions'}
          </button>
          
          {suggestions.length > 0 && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {suggestions.map((dest, idx) => (
                <DestinationCard key={idx} destination={dest} />
              ))}
            </div>
          )}
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Apply Filters
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <input
              type="number"
              placeholder="Max Budget"
              value={filters.budget}
              onChange={(e) => setFilters({ ...filters, budget: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Destination"
              value={filters.destination}
              onChange={(e) => setFilters({ ...filters, destination: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="Beach">Beach</option>
              <option value="Mountain">Mountain</option>
              <option value="City">City</option>
              <option value="Adventure">Adventure</option>
            </select>
          </div>
          
          <button
            onClick={applyFilters}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? 'Filtering...' : 'Apply Filters'}
          </button>
        </div>
      </div>
    );
  }

  if (step === 'filtered') {
    return (
      <div>
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Filtered Results</h2>
        
        {filteredDestinations.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <p className="text-gray-600 text-lg mb-4">No destinations match your filters</p>
            <button
              onClick={() => setStep('suggestions')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
            >
              Try Different Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDestinations.map((dest, idx) => (
              <DestinationCard key={idx} destination={dest} showBooking />
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
}

// Destination Card Component
function DestinationCard({ destination, showBooking }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition">
      <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500"></div>
      <div className="p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-2">{destination.name}</h3>
        <p className="text-gray-600 mb-4 flex items-center gap-1">
          <MapPin className="w-4 h-4" />
          {destination.country}
        </p>
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{destination.description}</p>
        
        <div className="flex justify-between items-center mb-4">
          <span className="flex items-center gap-1 text-green-600 font-bold">
            <DollarSign className="w-5 h-5" />
            {destination.cost.toFixed(2)}
          </span>
          <span className="flex items-center gap-1 text-yellow-600">
            <Star className="w-4 h-4 fill-current" />
            {destination.rating}
          </span>
        </div>
        
        <span className="inline-block bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm font-medium">
          {destination.category}
        </span>
        
        {showBooking && (
          <button className="w-full mt-4 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition">
            Book This Trip
          </button>
        )}
      </div>
    </div>
  );
}

// Trips View
function TripsView({ user, token }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      const result = await api.get(`/trips/${user.user_id}`, token);
      setTrips(result.trips || []);
    } catch (error) {
      console.error('Error fetching trips:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading trips...</div>;
  }

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-800 mb-6">My Trips</h2>
      
      {trips.length === 0 ? (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <Plane className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 text-lg">You haven't booked any trips yet</p>
          <p className="text-gray-500 mt-2">Start planning your first adventure!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-3">{trip.destination}</h3>
              <div className="space-y-2 text-gray-600">
                <p className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {trip.startDate} - {trip.endDate}
                </p>
                <p className="flex items-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Total: ${trip.totalbudget.toFixed(2)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}