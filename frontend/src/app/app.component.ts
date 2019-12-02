import { Component, OnInit, ViewChild } from '@angular/core';
import { MatHorizontalStepper, MatSnackBar } from '@angular/material';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AppService, VMStatus } from './app.service';
import { finalize, tap } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  @ViewChild('stepper', {static: true}) private stepperHandler: MatHorizontalStepper;
  private instanceId = null;
  private stateColors = {
    pending: 'text-muted-pending',
    stopping: 'text-muted-pending',
    stopped: 'text-muted-stopped',
    running: 'text-muted-running'
  };

  public isLoading = false;
  public currentState: VMStatus = {
    Code: 0,
    Name: 'Launching server',
    Raw: '',
    PublicIP: '',
    InstanceType: '',
    Region: ''
  };
  public currentStateColor: string = this.stateColors.pending;
  public credentialsForm: FormGroup;
  public instanceType = {
    label: 'Instance type',
    value: '',
    icon: 'computer'
  };
  public diskType = {
    label: 'Disk type',
    value: 'Magnetic disk',
    icon: 'memory'
  };
  public region = {
    label: 'Region',
    value: '',
    icon: 'location_on'
  };
  public isServerReady = false;
  public instanceLink = null;

  constructor(private formBuilder: FormBuilder,
              private service: AppService,
              private snackBar: MatSnackBar) {
  }

  get isCredentialsFormValid(): boolean {
    return this.credentialsForm.valid;
  }

  ngOnInit() {
    this.credentialsForm = this.formBuilder.group({
      clientId: ['', Validators.required],
      clientSecret: ['', Validators.required]
    });
  }

  get showActions(): boolean {
    return !this.isServerReady || this.currentState.Code !== 16;
  }

  get instanceUrl(): string {
    return `http://${ this.instanceLink }`;
  }

  public handleAWSCredentialsSubmit(): void {
    if (this.isCredentialsFormValid) {
      const {clientId, clientSecret} = this.credentialsForm.getRawValue();
      this.isLoading = true;
      this.service.createVM(clientId, clientSecret)
        .subscribe(data => {
        this.instanceId = data.InstanceId;
        this.instanceType.value = data.InstanceType;
        this.region.value = data.Region;
        this.stepperHandler.next();
        this.startStatusPolling();
      }, (res: HttpErrorResponse) => this.handleError(res));
    }
  }

  public stopServer(): void {
    if (this.isCredentialsFormValid) {
      this.isLoading = true;
      const {clientId, clientSecret} = this.credentialsForm.getRawValue();
      this.service.stopInstance(clientId, clientSecret, this.instanceId)
        .pipe(
          finalize(() => {
            this.startStatusPolling('stopped');
            this.isServerReady = false;
            this.isLoading = false;
          })
        )
        .subscribe(data => this.assign_status(data),
          (res: HttpErrorResponse) => this.handleError(res));
    }
  }


  private startStatusPolling(checkStatus = 'running'): void {
    const {clientId, clientSecret} = this.credentialsForm.getRawValue();
    this.service.getEC2Instance(clientId, clientSecret, this.instanceId, checkStatus)
      .pipe(
        tap(() => this.isLoading = true),
        finalize(() => {
          this.isLoading = false;
          this.isServerReady = true;
        })
      )
      .subscribe(data => this.assign_status(data),
        (res: HttpErrorResponse) => this.handleError(res));
  }

  private assign_status(data: VMStatus): void {
    this.currentState = data;
    this.currentStateColor = this.stateColors[data.Raw];
    if (this.currentStateColor === null) {
      this.currentStateColor = this.stateColors.stopped;
    }
    this.instanceLink = data.PublicIP;
    this.instanceType.value = data.InstanceType;
    this.region.value = data.Region;
  }

  private handleError(res: HttpErrorResponse) {
    let message = res.error && typeof res.error === 'string' ? res.error : res.message;
    if (res.status === 0) {
      message = 'Unknown error';
    }
    this.isLoading = false;
    this.snackBar.open(message, 'Dismiss', {
      duration: 5000,
    });
  }
}
