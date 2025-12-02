import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import QcCreatePage from './pages/QcCreatePage';
import QcDashboardPage from './pages/QcDashboardPage';
import QcReviewPage from './pages/QcReviewPage';
import ListingDetailPage from './pages/ListingDetailPage';
import GeoIdLookupPage from './pages/GeoIdLookupPage';
import MainLayout from './components/layout/MainLayout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="/internal/qc/new" element={<QcCreatePage />} />
          <Route path="/internal/qc/dashboard" element={<QcDashboardPage />} />
          <Route path="/internal/qc/review/:listingId" element={<QcReviewPage />} />
          <Route path="/listings/:listingId" element={<ListingDetailPage />} />
          {/* GeoID Short URL Routes - The "Instant Gratification" Feature */}
          {/* Matches: /AB1, /CGAB1, /29CGAB1, /CG.AB1, etc. */}
          <Route path="/:geoId" element={<GeoIdLookupPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
