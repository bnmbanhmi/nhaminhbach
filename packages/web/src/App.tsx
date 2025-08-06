import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import QcCreatePage from './pages/QcCreatePage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/admin/create" element={<QcCreatePage />} />
      </Routes>
    </Router>
  );
}

export default App;
