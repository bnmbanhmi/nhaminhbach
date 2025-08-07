import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import QcCreatePage from './pages/QcCreatePage';
import ListingDetailPage from './pages/ListingDetailPage';
import MainLayout from './components/layout/MainLayout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/internal/qc/new" element={<QcCreatePage />} />
          <Route path="/listings/:listingId" element={<ListingDetailPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
