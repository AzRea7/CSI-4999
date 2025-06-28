import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between p-4 bg-gray-100 shadow">
      <div className="space-x-4">
        <Link to="/" className="font-semibold">
          Home
        </Link>
        {user && (
          <>
            <Link to="/tasks">Tasks</Link>
            <Link to="/search">Search</Link>
            <Link to="/chatbot">ChatBot</Link>
          </>
        )}
      </div>

      {user ? (
        <div className="flex items-center space-x-4">
          <span>Welcome, {user.name}</span>
          <button
            onClick={logout}
            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      ) : (
        <Link
          to="/login"
          className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Login
        </Link>
      )}
    </nav>
  );
};

export default Navbar;
