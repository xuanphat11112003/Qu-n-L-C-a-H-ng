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
            <Navbar.Brand href="#h/"style={{ color: 'white' }}>
            <img src={"https://img.freepik.com/premium-vector/coffee-cup-vector-logo-design-te  mplate-premium-coffee-shop-logo_720103-917.jpg"} width="30" height="30" roundedCircle />
            Coffee 3ANHEM</Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="me-auto">
                <Link className='nav-link' to="/">Trang chủ
                </Link>
                {user===null?<>
                                                         
                    </>:<>
                    <Link className='nav-link' to="/giohang">Giỏ hàng
                        <Image src={"https://e7.pngegg.com/pngimages/81/559/png-clipart-shopping-cart-software-computer-icons-shopping-cart-text-retail-thumbnail.png"} width="30" height="30" roundedCircle />
                    </Link>
                    <Link className='nav-link' to="/donhang">Đơn hàng
                       
                    </Link>
                    </>}
                             
            </Nav>
            <Nav>
            {user===null?<>
                        <Link className='nav-link text-success' to="/login">Đăng nhập</Link>
                        <Link className='nav-link text-success' to="/register"> Đăng ký</Link>                                   
                    </>:<>
                         <Link className='nav-link text-success' to="/login">
                         <Image src={"https://img.freepik.com/free-vector/user-circles-set_78370-4704.jpg?size=626&ext=jpg"} width="30" height="30" roundedCircle />
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