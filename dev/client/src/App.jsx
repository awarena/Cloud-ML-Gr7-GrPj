import { Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './Components/Pages/Home'
import Login from './Components/Pages/Login'
import Signup from './Components/Pages/Signup'
import Test from './Components/Pages/Test'

function App() {
  return (
<Routes>
  <Route path="/" element={<Home/>}/>
  <Route path="/test" element={<Test/>}/>
  <Route path="/login" element={<Login/>}/>
  <Route path="/signup" element={<Signup/>}/></Routes>
  );
}

export default App;
