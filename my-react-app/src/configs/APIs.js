import axios from "axios"

export const BASE_URL= 'http://192.168.0.104:8000/'

export const endpoints ={
 'chitietsanpham': (id) => `sanpham/${id}/`,
 'comments': (id) => `sanpham/${id}/comments/`,
 'addcomment': (id) => `sanpham/${id}/add_comment/`,
 'sanpham': 'sanpham/',
 'register' :'users/',
 'current-user': 'users/current-user/',
 'login' : 'o/token/',
 'createHoaDon': 'hoadon/',
 'donhang': (id) => `hoadon/user-invoices/${id}/`,
}
export default axios.create({
    baseURL: BASE_URL
});