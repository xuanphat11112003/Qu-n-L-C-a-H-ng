
import 'bootstrap/dist/css/bootstrap.min.css';
import { useEffect, useState } from 'react';
import APIs, { endpoints } from './configs/APIs';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './layout/header';
import Footer from './layout/footer';
import { Container } from 'react-bootstrap';
import TrangChu from './components/TrangChu';

import Login from './components/Login';
import { createContext, useReducer } from 'react';
import MyUserReducer from './reducers/MyUserReducer';

import Register from './components/Register';




export const MyUserContext = createContext();
export const MyDispatchContext = createContext();

const App = () =>{
  const [loading, setLoading] = useState(true);
  const [user, dispatch] = useReducer(MyUserReducer, null);
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');     
      if (token) {
        try {
          // Gọi API để lấy thông tin người dùng
          let response = await APIs.get(endpoints['current-user'], {
            headers: {
                'Authorization': `Bearer ${token}` // Thêm token vào tiêu đề Authorization
            }
        });
        
        dispatch({ type: 'login', payload: response.data});
        } catch (error) {
          console.error('Error fetching user:', error);
          const username = localStorage.getItem('username');
          const avatar = localStorage.getItem('avatar');
          const first_name = localStorage.getItem('first');
          
          dispatch({
            type: 'login',
            payload: { 
                username: username, 
                avatar: avatar,
                first_name:first_name,
                access_token: token 
            }
        });
         
        }
      }
      
      
      setLoading(false);
    };

    loadUser();
  }, []);

  if (loading) {
    return <div>Loading...</div>; // Hiển thị trạng thái tải dữ liệu
  }

  return (
    <MyUserContext.Provider value={user}>
      <MyDispatchContext.Provider value={dispatch}>
          <BrowserRouter>
            <Header/>
            <Container>
              <Routes>
                <Route path='/' element={<TrangChu/>} />
               
                <Route path='/login' element={<Login/>} />
              
                <Route path='/register' element={<Register/>} />
              
              </Routes>
            </Container>
            <Footer/>
        </BrowserRouter>
      </MyDispatchContext.Provider>
    </MyUserContext.Provider>
    
   );
} 
export default App
