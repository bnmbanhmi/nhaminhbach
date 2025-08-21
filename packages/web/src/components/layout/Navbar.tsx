import { Link } from 'react-router-dom';
import { useState } from 'react';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-800 text-white w-full h-[10vh]">
      <div className="w-full h-full px-4 flex justify-between items-center">
        {/* Logo */}
        <div className="text-lg font-bold">
          <Link to="/" className="hover:text-gray-300">NhaMinhBach</Link>
        </div>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex gap-x-6">
          <Link to="/" className="hover:text-gray-300 transition-colors">Home</Link>
          <Link to="/internal/qc/dashboard" className="hover:text-gray-300 transition-colors">QC Dashboard</Link>
          <Link to="/internal/qc/new" className="hover:text-gray-300 transition-colors">QC Create</Link>
        </div>
        
        {/* Mobile Hamburger Button */}
        <button 
          onClick={toggleMenu}
          className="md:hidden flex flex-col justify-center items-center w-6 h-6 space-y-1"
          aria-label="Toggle menu"
        >
          <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></div>
          <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></div>
          <div className={`w-5 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></div>
        </button>
      </div>
      
      {/* Mobile Menu */}
      <div className={`md:hidden bg-gray-700 absolute top-full left-0 right-0 transition-all duration-300 overflow-hidden ${isMenuOpen ? 'max-h-48 opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="px-4 py-2 space-y-2">
          <Link 
            to="/" 
            className="block py-2 hover:text-gray-300 transition-colors"
            onClick={() => setIsMenuOpen(false)}
          >
            Home
          </Link>
          <Link 
            to="/internal/qc/dashboard" 
            className="block py-2 hover:text-gray-300 transition-colors"
            onClick={() => setIsMenuOpen(false)}
          >
            QC Dashboard
          </Link>
          <Link 
            to="/internal/qc/new" 
            className="block py-2 hover:text-gray-300 transition-colors"
            onClick={() => setIsMenuOpen(false)}
          >
            QC Create
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
