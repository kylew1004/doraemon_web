import React, { useState } from "react";
import { RouterProvider, createBrowserRouter, Outlet } from 'react-router-dom';
import {tokenLoader, checkAuthLoader} from './util/auth';
import Welcome, {action as authAction} from "./page/Welcome.js";
import {action as logoutAction} from './page/Logout.js';
import Assets from './page/Assets.js';
import RootLayout from "./components/Root.js";
import StyleTransfer from './page/StyleTransfer.js';
import PoseTransfer from './page/PoseTransfer.js';
import CreateNew from './page/CreateNew.js';
import Train from './page/Train.js';

 
const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    // errorElement: <ErrorPage />,
    id:'root',
    loader: tokenLoader,
    children: [
      { index: true, element: <Assets /> },
      {
        path: 'assets',
        element: <Assets />,
        // action: authAction
      },
      {
        path: 'createNew',
        element: <Outlet />,
        // action: authAction,
        children:[
          { index: true, element: <CreateNew /> },
          {
            path: 'styleTransfer',
            element: <StyleTransfer />,
            // action: authAction,
          },
          {
            path: 'poseTransfer',
            element: <PoseTransfer />,
            // action: authAction,
          },

        ]
      },
      {
        path: 'train',
        element: <Train />,
        // action: authAction,
      },
      {
        path: 'logout',
        action: logoutAction,
      }
    ],
  },
  {
    path: '/auth',
    element: <Welcome />,
    // errorElement: <ErrorPage />,
    action: authAction

  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;