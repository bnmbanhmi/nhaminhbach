import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

const MainLayout = () => {
  return (
    <div>
      <Navbar />
      <main className="pt-[10vh]">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
