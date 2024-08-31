// src/components/ChiTietSanPham.js
import { useEffect, useState, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { Button, ListGroup, Form } from 'react-bootstrap';
import APIs, { endpoints } from '../configs/APIs';
import {  MyUserContext } from "../App";

const ChiTietSanPham = () => {
    const [sanpham, setSanPham] = useState(null);
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const id = queryParams.get('id');
    const [quantity, setQuantity] = useState(1);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [commentContent, setCommentContent] = useState('');
    const [showAllComments, setShowAllComments] = useState(false);
    const [visibleComments, setVisibleComments] = useState([]);
    const user = useContext(MyUserContext);
    useEffect(() => {
        const loadSanPham = async () => {
            try {
                let res = await APIs.get(endpoints.chitietsanpham(id));
                setSanPham(res.data);
               
            } catch (ex) {
                console.error(ex);
            }
        };
        const loadComments = async () => {
            try {
                let res = await APIs.get(endpoints.comments(id));
                // Đảo ngược danh sách bình luận để hiển thị bình luận mới nhất đầu tiên
                const reversedComments = res.data.reverse();
                setComments(reversedComments);
                setVisibleComments(reversedComments.slice(0, 4)); // Hiển thị 4 bình luận cuối cùng
            } catch (ex) {
                console.error(ex);
            }
        };
        loadSanPham();
        loadComments()
    }, [id]);
   

    // Hàm để giảm số lượng sản phẩm

    const handleDecrease = () => {
        setQuantity(prevQuantity => Math.max(prevQuantity - 1, 1));
    };

    // Hàm để tăng số lượng sản phẩm
    const handleIncrease = () => {
        setQuantity(prevQuantity => prevQuantity + 1);
    };
    const handleShowMoreComments = () => {
        setShowAllComments(true);
        setVisibleComments(comments);
    };
    const handleAddComment = async () => {
        try {
            if (!user) {
                alert('You need to be logged in to add a comment.');
                return;
            }
            if (!commentContent) {
                alert('Please enter a comment.');
                return;
            }
            const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');     
            let response = await APIs.post(endpoints.addcomment(id), { content: commentContent }, {
                headers: {
                    'Authorization': `Bearer ${token}` // Thay đổi tùy theo phương thức xác thực bạn sử dụng
                }
            });
            const res = await APIs.get(endpoints.comments(id));
            const newComments = [response.data, ...res.data];
            setComments(res.data);
            setVisibleComments(res.data.slice(0, 4)); // Hiển thị bình luận mới nhất và 4 bình luận đầu tiên

            setCommentContent(''); // Xóa nội dung bình luận sau khi gửi thành công
            if (window.confirm('Bình luận đã được gửi thành công. Bạn có muốn làm mới trang không?')) {
                window.location.reload(); // Làm mới trang
            }
        } catch (error) {
            console.error("Error adding comment:", error);
        }
    };
    if (!sanpham) return <div>Loading...</div>;

    return (
        <div className="d- justify-content-center mt-4">
            <div className="d-flex" style={{ maxWidth: '1000px', width: '100%' }}>
                <div className="flex-shrink-0" style={{ width: '50%' }}>
                    <img 
                        src={sanpham.hinh_anh} 
                        alt={sanpham.ten_sp} 
                        style={{ width: '100%', height: 'auto', objectFit: 'cover' }} 
                    />
                </div>
                <div className="flex-grow-1" style={{ padding: '20px' }}>
                    <h2>{sanpham.ten_sp}</h2>
                    <p><strong>Giá: {sanpham.don_gia || 'N/A'} đồng</strong></p>
                    <p>
                        <strong>
                            Tình trạng: {sanpham.active ? 'Còn' : 'Tạm hết'}
                        </strong>
                    </p>
                    <div className="d-flex align-items-center mb-3">
                        <Button variant="secondary" onClick={handleDecrease}>-</Button>
                        <span className="mx-3">{quantity}</span>
                        <Button variant="secondary" onClick={handleIncrease}>+</Button>
                    </div>
                    <Button variant="success">Thêm vào giỏ hàng</Button>
                </div>
            </div>
            <div className="mt-4" style={{ maxWidth: '1000px', width: '100%' }}>
                <h3>Bình luận</h3>
                {comments.length > 4 && !showAllComments && (
                    <Button className="mt-2" variant="link" onClick={handleShowMoreComments}>
                        Xem thêm bình luận
                    </Button>
                )}
                <ListGroup>
                {visibleComments.length > 0 ? (
                    visibleComments.map((comment, index) => (
                        <ListGroup.Item key={index}>
                            <div key={comment.id} className="mb-3">
                                <div className="d-flex justify-content-between">
                                    <div>
                                        <strong>{comment.user.username}:</strong>
                                        <p>{comment.content}</p>
                                    </div>
                                    <div className="text-end">
                                        <p className="text-muted">Thời gian:
                                            {new Date(comment.created_date).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </ListGroup.Item>
                    ))
                    ) : (
                        <ListGroup.Item>Chưa có bình luận nào.</ListGroup.Item>
                        
                    )}
                      {user && (
                        <div className="mt-4">
                            <Form>
                                <Form.Group controlId="commentContent">
                                    <Form.Label>Thêm bình luận</Form.Label>
                                    <Form.Control
                                        as="textarea"
                                        rows={3}
                                        value={commentContent}
                                        onChange={(e) => setCommentContent(e.target.value)}
                                    />
                                </Form.Group>
                                <Button variant="primary" onClick={handleAddComment}>Gửi</Button>
                            </Form>
                        </div>
                )}
                
                </ListGroup>
            </div>
        </div>
    );
};

export default ChiTietSanPham;
