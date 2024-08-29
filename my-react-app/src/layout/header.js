import { useContext } from "react";
import { Button, Container, Image, Nav, Navbar } from "react-bootstrap";
import { Link } from "react-router-dom";
import { MyDispatchContext, MyUserContext } from "../App";
import '../style/header.css'
const Header =() =>{
    const user = useContext(MyUserContext);
    const dispatch = useContext(MyDispatchContext); // Lấy dispatch từ context

    const handleLogout = () => {
        dispatch({ type: 'logout' }); // Gọi dispatch với hành động logout
    };
    return(
        <>
        <Navbar collapseOnSelect expand="lg" className="custom-navbar">
        <Container>
            <Navbar.Brand href="#h/">Cafe 3ANHEM</Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
                <Link className='nav-link' to="/">Trang chủ</Link>
              
                             
            </Nav>
            <Nav>
            {user===null?<>
                        <Link className='nav-link text-success' to="/login">Đăng nhập</Link>
                        <Link className='nav-link text-success' to="/register"> Đăng ký</Link>                                   
                    </>:<>
                         <Link className='nav-link text-success' to="/login">
                         <Image src={user.avatar} width="30" height="30" roundedCircle />
                              {user.first_name}!</Link>
                              <Button variant='danger' onClick={handleLogout}>Đăng xuất</Button>
                    </>}
            </Nav>
            </Navbar.Collapse>
        </Container>
        </Navbar>
        </>
    );
}
export default Header;