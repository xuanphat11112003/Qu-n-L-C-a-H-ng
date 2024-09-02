import { Button, Card } from 'react-bootstrap';
import { useEffect, useState } from 'react';
import APIs, { endpoints } from '../configs/APIs';
import { useNavigate } from 'react-router';
import '../style/trangchu.css'

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
                    <div className="card-img-flip-container">
                        <div className="card-img-flip">
                            <Card.Img variant="top" src={"https://res.cloudinary.com/dzfnj3hdq/"+item.hinh_anh} />
                            <Card.Img variant="top" src="https://img.freepik.com/premium-vector/coffee-cup-vector-logo-design-template-premium-coffee-shop-logo_720103-917.jpg" className="back" />
                        </div>
                    </div>
                    <Card.Body>
                        <Card.Title>{item.ten_sp || 'Card Title'}</Card.Title>
                        <Card.Text>{parseFloat(item.don_gia).toLocaleString('vi-VN', { minimumFractionDigits: 0 })}đ</Card.Text>

                       
                        <Button variant="primary" onClick={() => chiTiet(item.id)}>Xem chi tiết</Button>
                    </Card.Body>
                </Card>
           
           
            ))}
        </div>
    );
};

export default TrangChu;
