import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="text-lg font-bold">
          <Link to="/">NhaMinhBach</Link>
        </div>
        <div className="flex gap-x-4">
          <Link to="/" className="hover:text-gray-300">Home</Link>
          <Link to="/internal/qc/new" className="hover:text-gray-300">QC Dashboard</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
