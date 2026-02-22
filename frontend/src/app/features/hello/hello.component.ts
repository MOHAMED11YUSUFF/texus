import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-hello',
  templateUrl: './hello.component.html'
})
export class HelloComponent implements OnInit {

  message: string = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getHello().subscribe((res: string) => {
      this.message = res;
    });
  }
}