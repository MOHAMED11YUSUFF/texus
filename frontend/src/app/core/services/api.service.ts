import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private baseUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  getHello(): Observable<string> {
    return this.http.get(`${this.baseUrl}/api/sample/`, {
      responseType: 'text'
    });
  }

  uploadFile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);  // 'file' must match FastAPI parameter name

    return this.http.post(`${this.baseUrl}/api/file/`, formData);
  }
}