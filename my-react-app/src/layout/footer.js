// const Footer =() =>{
//     return(
//         <></>
//     );
// }
// export default Footer;
import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

import '../style/footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <Container>
        <Row>
          {/* Logo và mô tả */}
          <Col md={3} className="footer-logo">
            <img src="https://img.freepik.com/premium-vector/coffee-cup-vector-logo-design-template-premium-coffee-shop-logo_720103-917.jpg" alt="Logo" className="footer-logo-img" />
            <p className="footer-description">
              Chúng tôi cung cấp các giải pháp công nghệ tiên tiến để phát triển doanh nghiệp của bạn.
            </p>
          </Col>

          {/* Liên kết nhanh */}
          <Col md={3} className="footer-links">
            <h5>Liên Kết Nhanh</h5>
            <ul className="list-unstyled">
              <li><a href="/about">Về Chúng Tôi</a></li>
              <li><a href="/services">Dịch Vụ</a></li>
              <li><a href="/contact">Liên Hệ</a></li>
              <li><a href="/blog">Blog</a></li>
            </ul>
          </Col>

          {/* Thông tin liên hệ */}
          <Col md={3} className="footer-contact">
            <h5>Liên Hệ</h5>
            <p>Tân Bình, Thành phố Hồ Chí Minh</p>
            <p>Email: huythua0@gmail.com</p>
            <p>Phone: +84 123 456 789</p>
          </Col>

          {/* Mạng xã hội */}
          <Col md={3} className="footer-social">
            <h5>Theo Dõi Chúng Tôi</h5>
            
          </Col>
        </Row>

        <Row className="footer-bottom">
          <Col md={12} className="text-center">
            <p className="footer-copyright">
              &copy; 2024 Trần Huy Thừa. Tất cả các quyền được bảo lưu.
            </p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
