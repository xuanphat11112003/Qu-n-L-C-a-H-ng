// src/components/OrderPage.js
import React, { useState, useEffect, useContext } from 'react';
import { Table, Button, Badge  } from 'react-bootstrap';
import APIs, { endpoints } from '../configs/APIs';
import { MyUserContext } from '../App';

const DonHang = () => {
    const user = useContext(MyUserContext); // Lấy thông tin user từ context
    const [orders, setOrders] = useState([]);

    useEffect(() => {
        const fetchOrders = async () => {
            const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
            try {
                const response = await APIs.get(endpoints.donhang(user.id), {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setOrders(response.data); // Gán dữ liệu đơn hàng từ API
            } catch (error) {
                console.error("Error fetching orders:", error);
            }
        };

        if (user?.id) {  // Chỉ gọi API nếu đã có thông tin user
            fetchOrders();
        }
    }, [user]);
    // Hàm format tiền Việt Nam Đồng
    const formatCurrency = (amount) => {
        return parseFloat(amount).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
    };

    // Hàm format ngày tháng
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    };

    // Hàm format trạng thái
    const renderStatusBadge = (status) => {
        switch (status) {
            case 'prep':
                return <Badge bg="warning" text="dark">Đang chuẩn bị</Badge>;
            case 'shipped':
                return <Badge bg="info">Đã giao hàng</Badge>;
            case 'delivered':
                return <Badge bg="success">Đã giao</Badge>;
            case 'cancelled':
                return <Badge bg="danger">Đã hủy</Badge>;
            default:
                return <Badge bg="secondary">Không xác định</Badge>;
        }
    };
    return (
        <div className="container mt-5">
            <h2 className="text-center mb-4">Danh sách hóa đơn</h2>

            {orders.length === 0 ? (
                <p>Bạn chưa có đơn hàng nào.</p>
            ) : (
                <Table striped bordered hover>
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Ngày lập</th>
                            <th>Tổng tiền</th>
                            <th>Ghi chú</th>
                            <th>Trạng thái</th>
                            <th>Phương thức thanh toán</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders.map((order) => (
                            <tr key={order.id}>
                                <td>{order.id}</td>
                                <td>{formatDate(order.ngay_lap)}</td>
                                <td>{formatCurrency(order.tong_tien)}</td>
                                <td>{order.ghi_chu || 'Không có'}</td>
                                <td>{renderStatusBadge(order.trang_thai)}</td>
                                <td>{order.phuong_thuc_thanh_toan === 'cash' ? 'Tiền mặt' : 'Khác'}</td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            )}
        </div>
    );
};

const handleViewDetails = (orderId) => {
    // Xử lý sự kiện xem chi tiết đơn hàng, ví dụ: điều hướng sang trang chi tiết đơn hàng
    window.location.href = `/order-details/${orderId}`;
};

export default DonHang;
