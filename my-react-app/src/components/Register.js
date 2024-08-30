
import { useRef, useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";
import { useNavigate } from "react-router";
import APIs, { endpoints } from "../configs/APIs";

const Register = () => {
    const [user, setUser] = useState({});
    const [err, setErr] = useState();
    const nav = useNavigate();

    const register = async (e) => {
        e.preventDefault();

        if (user.password !== user.confirm) {
            setErr("Mật khẩu KHÔNG khớp!");
        } else {
            let form = new FormData();
            for (let key in user)
                if (key !== 'confirm')
                    form.append(key, user[key]);        
            let res = await APIs.post(endpoints['register'], form, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            if (res.status === 201)
                nav("/login");
        }
    }

    const change = (e, field) => {
        setUser({...user, [field]: e.target.value})
    }

    return (
        <>
        <div  className="modal show"
      style={{ display: 'block', position: 'initial' }}>
        <Modal.Dialog>
            <Modal.Header >
            <Modal.Title style={{ color: 'green' }}>ĐĂNG KÝ NGƯỜI DÙNG BUSMAP</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            {err && <Alert variant="danger">{err}</Alert>}

            <Form onSubmit={register} method="post">
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                    <Form.Label>Tên</Form.Label>
                    <Form.Control type="text" placeholder="Tên..." value={user.first_name} onChange={e => change(e, "first_name")} />
                </Form.Group>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput2">
                    <Form.Label>Họ và chữ lót</Form.Label>
                    <Form.Control type="text" placeholder="Họ và chữ lót..." value={user.last_name} onChange={e => change(e, "last_name")} />
                </Form.Group>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control type="email" placeholder="Email..." value={user.email} onChange={e => change(e, "email")} />
                </Form.Group>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput5">
                    <Form.Label>Tên đăng nhập</Form.Label>
                    <Form.Control type="text" placeholder="Tên đăng nhập..." value={user.username} onChange={e => change(e, "username")} />
                </Form.Group>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput6">
                    <Form.Label>Mật khẩu</Form.Label>
                    <Form.Control type="password" placeholder="Mật khẩu..." value={user.password} onChange={e => change(e, "password")}  />
                </Form.Group>
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput7">
                    <Form.Label>Xác nhận mật khẩu</Form.Label>
                    <Form.Control type="password" placeholder="Xác nhận mật khẩu..." value={user.confirm} onChange={e => change(e, "confirm")}  />
                </Form.Group>       
                <Form.Group className="mb-3" controlId="exampleForm.ControlInput9">
                    <Button type="submit" variant="info">Đăng ký</Button>
                </Form.Group>
            </Form>
        </Modal.Body>         
        </Modal.Dialog>
        </div>
        </>
    )
}

export default Register;