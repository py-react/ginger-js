import React, {useRef} from 'react'
import { useEffect } from 'react';
import {Link} from "react-router-dom";
import useNavigate from '@/libs/navigate';


function CustomLink(props) {
    const navigate = useNavigate();
    const ref = useRef(null)

    useEffect(()=>{
        const navigation = function(e){
            e.preventDefault()
            navigate(e.target.href)
        }
        if(ref.current){
            ref.current.addEventListener("click",navigation,null)
        }
        return ()=>{
            if(ref.current){
                ref.current.removeEventListener('click',navigation,null)
            }
        }
    },[])
    return (
        <Link ref={ref} {...props} />
    )
}

export default CustomLink