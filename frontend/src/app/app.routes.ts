import { Routes } from '@angular/router';
import { HelloComponent } from './features/hello/hello.component';
import { FileComponent } from './features/file/file.component';


export const routes: Routes = [
  { path: 'hello', component: HelloComponent },
  { path: 'file', component: FileComponent },
];