import axios from "axios"

export const BASE_URL= 'http://192.168.2.8:8000/'

export const endpoints ={
 'chitietsanpham': (id) => `sanpham/${id}/`,
 'comments': (id) => `sanpham/${id}/comments/`,
 'addcomment': (id) => `sanpham/${id}/add_comment/`,
 'sanpham': 'sanpham/',
 'register' :'users/',
 'current-user': 'users/current-user/',
 'login' : 'o/token/',
 'createHoaDon': 'hoadon/create_hoa_don/'
}
export default axios.create({
    baseURL: BASE_URL
});