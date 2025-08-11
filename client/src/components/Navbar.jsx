import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="w-screen bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-screen-2xl mx-auto px-6 py-3 flex items-center justify-between">
        {/* Left Section (Brand + Links) */}
        <div className="flex items-center space-x-8">
          <Link
            to="/"
            className="text-xl font-bold text-red-500 tracking-tight"
          >
            HomeFinder
          </Link>

          {user && (
            <div className="flex items-center space-x-6 text-gray-700 font-medium">
              <Link to="/tasks" className="hover:text-red-500 transition">
                Tasks
              </Link>
              <Link to="/search" className="hover:text-red-500 transition">
                Search
              </Link>
              <Link to="/chatbot" className="hover:text-red-500 transition">
                ChatBot
              </Link>
              <Link to="/analytics" className="hover:text-red-500 transition">
                Analytics
              </Link>
            </div>
          )}
        </div>

        {/* Right Section (Auth) */}
        <div className="flex items-center space-x-4">
          {user ? (
            <>
              <span className="text-gray-600">
                Hi, <span className="font-semibold">{user.name}</span>
              </span>
              <button
                onClick={logout}
                className="px-4 py-2 rounded-full border border-gray-300 hover:border-red-500 text-gray-700 hover:text-red-500 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 rounded-full bg-red-500 hover:bg-red-600 text-white transition"
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
