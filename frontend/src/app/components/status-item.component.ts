import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-status-item',
  templateUrl: './status-item.component.html',
  styleUrls: ['./status-item.component.css']
})
export class StatusItemComponent {
  @Input() label: string;
  @Input() value: string;
  @Input() icon: string;
}
