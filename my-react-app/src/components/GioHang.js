// src/components/CartPage.js
import React, { useState, useEffect, useContext } from 'react';
import { Button, Table, Modal, Form } from 'react-bootstrap';
import APIs, { endpoints } from '../configs/APIs';
import { MyUserContext } from '../App';

const CartPage = () => {
    const user = useContext(MyUserContext);
    const [cart, setCart] = useState([]);
    const [products, setProducts] = useState([]);
    const [totalPrice, setTotalPrice] = useState(0);
    const [showInvoice, setShowInvoice] = useState(false);
    const [invoiceData, setInvoiceData] = useState({    
        ghi_chu: '',
        tong_tien: '',
        khach_hang: 1, // Placeholder ID, should be dynamic based on logged-in user
        nhan_vien: 1,
        chi_tiet: []
    });

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
                setCart(cartItems);

                const productIds = cartItems.map(item => item.id);
                if (productIds.length > 0) {
                    const responses = await Promise.all(productIds.map(id => APIs.get(endpoints.chitietsanpham(id))));
                    const productsData = responses.map(res => res.data);
                    setProducts(productsData);

                    const total = cartItems.reduce((sum, item) => {
                        const product = productsData.find(p => p.id === item.id);
                        return sum + (product ? product.don_gia * item.quantity : 0);
                    }, 0);
                    setTotalPrice(total);
                }
            } catch (error) {
                console.error("Error fetching products:", error);
            }
        };

        fetchProducts();
    }, []);

    const handleRemoveFromCart = (id) => {
        const updatedCart = cart.filter(item => item.id !== id);
        localStorage.setItem('cart', JSON.stringify(updatedCart));
        setCart(updatedCart);
        setProducts(products.filter(product => product.id !== id));
        const total = updatedCart.reduce((sum, item) => {
            const product = products.find(p => p.id === item.id);
            return sum + (product ? product.don_gia * item.quantity : 0);
        }, 0);
        setTotalPrice(total);
    };

    const handleShowInvoice = () => {
        const invoiceDetails = cart.map(item => ({
            san_pham: item.id,
            so_luong: item.quantity
        }));

        setInvoiceData({
            ghi_chu: '', // Can be updated with user input
            tong_tien: totalPrice.toFixed(2), // Ensure the total price is formatted correctly
            khach_hang: 1, // Placeholder customer ID, should be updated based on logged-in user
            nhan_vien: 1,
            chi_tiet: invoiceDetails
        });
        setShowInvoice(true);
    };

    const handlePostInvoice = async () => {
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');  
    
        
    
        try {
            const response = await APIs.post(endpoints.createHoaDon, invoiceData, {
                headers: {
                    'Authorization': `Bearer ${token}`, // Thêm token vào header
                    'Content-Type': 'application/json'  // Đảm bảo kiểu dữ liệu là JSON
                }
            });
            console.log("Response from server:", invoiceData);
            const invoiceId = response.data.id; // Lấy ID hóa đơn
    
            // Xóa giỏ hàng và cập nhật trạng thái
            localStorage.removeItem('cart');
            setCart([]);
            setProducts([]);
            setTotalPrice(0);
            setShowInvoice(false);
    
            alert('Hóa đơn đã được tạo thành công.');
    
            // Redirect hoặc hiển thị các tùy chọn thanh toán
            // Example: window.location.href = `/payment?invoiceId=${invoiceId}`;
        } catch (error) {
            console.error("Error posting invoice:", error.response ? error.response.data : error.message);
            alert('Có lỗi xảy ra khi tạo hóa đơn.');
        }
    };
    
    

    return (
        <div className="container mt-4">
            <h2>Giỏ hàng</h2>
            {cart.length === 0 ? (
                <p>Giỏ hàng của bạn đang rỗng.</p>
            ) : (
                <div>
                    <Table striped bordered hover>
                        <thead>
                            <tr>
                                <th>Ảnh</th>
                                <th>Tên sản phẩm</th>
                                <th>Số lượng</th>
                                <th>Giá</th>
                                <th>Tổng</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {cart.map((item) => {
                                const product = products.find(p => p.id === item.id);
                                return product ? (
                                    <tr key={item.id}>
                                        <td>
                                            <img
                                                src={"https://res.cloudinary.com/dzfnj3hdq/" + product.hinh_anh}
                                                alt={product.ten_sp}
                                                style={{ width: '100px', height: 'auto' }}
                                            />
                                        </td>
                                        <td>{product.ten_sp}</td>
                                        <td>{item.quantity}</td>
                                        <td>{product.don_gia.toLocaleString('vi-VN')}đ</td>
                                        <td>{(product.don_gia * item.quantity).toLocaleString('vi-VN')}đ</td>
                                        <td>
                                            <Button variant="danger" onClick={() => handleRemoveFromCart(item.id)}>Xóa</Button>
                                        </td>
                                    </tr>
                                ) : null;
                            })}
                        </tbody>
                    </Table>
                    <h4>Tổng giá: {totalPrice.toLocaleString('vi-VN')}đ</h4>
                    <Button variant="primary" onClick={handleShowInvoice}>Thanh toán</Button>
                </div>
            )}

            {/* Modal for Invoice */}
            <Modal show={showInvoice} onHide={() => setShowInvoice(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Hóa đơn</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group controlId="formNote">
                            <Form.Label>Ghi chú</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Nhập ghi chú (nếu có)"
                                value={invoiceData.ghi_chu}
                                onChange={(e) => setInvoiceData({ ...invoiceData, ghi_chu: e.target.value })}
                            />
                        </Form.Group>
                        <h4>Tổng tiền: {invoiceData.tong_tien}đ</h4>
                        <Table striped bordered hover>
                            <thead>
                                <tr>
                                    <th>Tên sản phẩm</th>
                                    <th>Số lượng</th>
                                    <th>Giá</th>
                                    <th>Tổng</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoiceData.chi_tiet.map((item, index) => {
                                    const product = products.find(p => p.id === item.san_pham);
                                    return product ? (
                                        <tr key={index}>
                                            <td>{product.ten_sp}</td>
                                            <td>{item.so_luong}</td>
                                            <td>{product.don_gia.toLocaleString('vi-VN')}đ</td>
                                            <td>{(product.don_gia * item.so_luong).toLocaleString('vi-VN')}đ</td>
                                        </tr>
                                    ) : null;
                                })}
                            </tbody>
                        </Table>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowInvoice(false)}>
                        Đóng
                    </Button>
                    <Button variant="primary" onClick={handlePostInvoice}>
                        Thanh toán
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default CartPage;
