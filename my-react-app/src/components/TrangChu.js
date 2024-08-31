import { Button, Card } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import APIs, { endpoints } from '../configs/APIs';
import { useNavigate } from 'react-router';

const TrangChu = () => {
    const [sanpham, setSanPham] = useState([]);
    const navigate = useNavigate();

    const chiTiet = (id) => {
        navigate(`/sanpham/chitietsanpham?id=${id}`);
    };

    useEffect(() => {
        loadSanPham();
    }, []);

    const loadSanPham = async () => {
        try {
            let res = await APIs.get(endpoints['sanpham']);
            setSanPham(res.data);
            console.log("Thanh cong");
        } catch (ex) {
            console.error(ex);
        }
    };

    return (
        <div className="d-flex flex-wrap">
            {sanpham.map((item, index) => (
                <Card key={index} style={{ width: '18rem', margin: '10px' }}>
                    <Card.Img variant="top" src={item.hinh_anh} />
                    <Card.Body>
                        <Card.Title>{item.ten_sp || 'Card Title'}</Card.Title>
                        <Card.Text>{item.don_gia || 'No description available.'}</Card.Text>
                        <Button   variant="success">Thêm vào giỏ hàng</Button>
                        <Button variant="primary" onClick={() => chiTiet(item.id)}>Xem chi tiết</Button>
                    </Card.Body>
                </Card>
            ))}
        </div>
    );
};

export default TrangChu;
