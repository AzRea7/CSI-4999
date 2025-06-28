import { useAuth } from "../AuthContext";

const HomeDashboard = () => {
  const { user } = useAuth();

  return (
    <div>
      <h2>🏡 Home Dashboard</h2>
      <p>Welcome back, {user?.name} 👋</p>
    </div>
  );
};

export default HomeDashboard;
