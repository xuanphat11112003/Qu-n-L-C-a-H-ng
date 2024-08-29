import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import { useState,  useContext} from 'react';
import APIs, { endpoints } from '../configs/APIs';
import { MyDispatchContext, MyUserContext } from "../App";
import { Navigate } from 'react-router';


const Login =() =>{
    const user = useContext(MyUserContext);
    const dispatch = useContext(MyDispatchContext);
    const [username, setUsername] = useState();
    const [password, setPassword] = useState();
    const [rememberMe, setRememberMe] = useState(false);
   
    if (user !== null)
        return <Navigate to="/" />
    const checkNhoMatKhau = (e) => {
        setRememberMe(e.target.checked);
    };
    const login = async (e) => {
        e.preventDefault();
        let formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('client_id', 'gsGoNBhyFQpO0ro40t4wOaBzl3v0iof8oWfvn4rM');
        formData.append('client_secret', 'nvw3W4rep3nw063Hx31PXrLrNH5G6QkeELJv6qpwOks6bRsUh8a4AaGzuNBcTIvbwJXq0MHJQZUIdCvHUF81cRqsqJyDxsDPFkl9D3zN3Wjh9qU2a5C8RQtSkf4NNFMR');
        formData.append('grant_type', 'password');

        try {
            let res = await APIs.post(endpoints['login'], formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
    
            const token = res.data.access_token; 
    
            if (rememberMe) {
                // Lưu token vào localStorage nếu người dùng tick "Nhớ mật khẩu"
                localStorage.setItem('access_token', token);
                localStorage.setItem('username', username); 
                
            } else {
                // Nếu không tick thì chỉ lưu vào sessionStorage (chỉ duy trì trong phiên làm việc)
                sessionStorage.setItem('access_token', token);
            }
    
            
            let response = await APIs.get(endpoints['current-user'], {
                headers: {
                    'Authorization': `Bearer ${token}` // Thêm token vào tiêu đề Authorization
                }
            });
            dispatch({ type: 'login', payload: response.data});
            
        } catch (error) {
            console.error("Error:", error.response ? error.response.data : error.message);
        }
    }
   
   
    return(
        <>
        <div
      className="modal show"
      style={{ display: 'block', position: 'initial' }}
        >
        <Modal.Dialog>
            <Modal.Header >
            <Modal.Title style={{ color: 'green' }}>Đăng nhập người dùng</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            <Form onSubmit={login}>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                    <Form.Label>Tài khoản</Form.Label>
                    <Form.Control placeholder="Nhập tài khoản" value={username} onChange={e => setUsername(e.target.value)} />                 
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicPassword">
                    <Form.Label>Mật khẩu</Form.Label>
                    <Form.Control type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)}/>
                </Form.Group>

                <Form.Group className="mb-3" controlId="formBasicCheckbox">
                    <Form.Check type="checkbox" label="Nhớ mật khẩu" onChange={checkNhoMatKhau}/>
                </Form.Group>

                <Button  variant="success" type="submit" className="w-100 mb-2"  >
                    Đăng nhập
                </Button>

                <Form.Text className="text-muted d-block mb-2">
                   Nếu bạn chưa có tài khoản
                    </Form.Text>

                <Button variant="primary" className="w-100 mb-2" >
                    Đăng kí
                </Button>
               
            </Form>
            </Modal.Body>         
        </Modal.Dialog>
        </div>
       
        </>
    );
}
export default Login;