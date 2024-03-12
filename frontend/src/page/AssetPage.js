import { Link, useSearchParams, useLocation, Outlet } from 'react-router-dom';
import {useEffect} from 'react';

export default function Assets(){
    const [searchParams, setSearchParams] = useSearchParams();
    const location = useLocation();
    const passLength = location.pathname.split('/').length;

    useEffect(() => {
        if (!searchParams.get('mode')) {
          searchParams.set("mode", "Scenes");
          setSearchParams(searchParams);
        }
    }, [searchParams, setSearchParams]);

    const active = searchParams.get('mode')==='Scenes' ? 'Scenes' : 'Characters';
    const inactive = active==='Scenes' ? 'Characters' : 'Scenes';


    return <div className="flex flex-col  w-full h-full">

            <div className="relative flex justify-center items-center w-full m-auto py-3">
                <Link to={`?mode=${inactive}`} hidden={passLength===4} className={ `button h-12 w-[160px] absolute left-1/2 transform -translate-x${active==="Characters"?"":"-"}-3/4 bg-gray-300 text-gray-500 rounded-full`}>
                    <p className="font-bold text-center pt-3">{inactive}</p>
                </Link>
                <Link to={`?mode=${active}`} hidden={passLength===4} className={`button h-12 w-[160px] absolute left-1/2 transform -translate-x-${active==="Characters"?"-":""}3/4 bg-yellow-500 text-black rounded-full`}>
                <p className="font-bold text-center pt-3">{active}</p>
                </Link>
            </div>



            <div className="flex flex-row p-6 gap-7 flex-wrap overflow-auto bg-white bg-opacity-30 m-auto rounded-xl w-11/12 h-5/6 mt-0">
                <Outlet />
            </div>

    
</div>
}