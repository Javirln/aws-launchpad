import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { interval, Observable } from 'rxjs';
import { switchMap, takeWhile } from 'rxjs/operators';
import { environment } from '../environments/environment';

export interface VMStatus {
  Code: number;
  Name: string;
  Raw: string;
  PublicIP: string;
  InstanceType: string;
  Region: string;
}

export interface InstanceDetails {
  InstanceId: string;
  InstanceType: string;
  Region: string;
}

@Injectable()
export class AppService {
  private API_DOMAIN = environment.apiDomain;

  constructor(private httpClient: HttpClient) {
  }

  public stopInstance(clientId: string, clientSecret: string, instanceId: string): Observable<VMStatus> {
    return this.httpClient.post<VMStatus>(`${ this.API_DOMAIN }/ec2/stop-instance`, {
      client_id: clientId,
      client_secret: clientSecret,
      instance_id: instanceId
    });
  }

  public createVM(clientId: string, clientSecret: string): Observable<InstanceDetails> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };

    return this.httpClient.post<InstanceDetails>(`${ this.API_DOMAIN }/ec2/create-vm`, {
      client_id: clientId,
      client_secret: clientSecret
    }, httpOptions);
  }


  public getEC2Instance(clientId: string, clientSecret: string, instanceId: string, checkStatus = 'running'): Observable<VMStatus> {
    return interval(10000)
      .pipe(
        switchMap(() => this.httpClient.post<VMStatus>(`${ this.API_DOMAIN }/ec2/check-status`, {
          client_id: clientId,
          client_secret: clientSecret,
          instance_id: instanceId
        })),
        takeWhile(res => res.Raw !== checkStatus, true)
      );
  }
}
