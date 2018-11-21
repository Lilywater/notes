#!/usr/bin/env python
"""
TTCN3 component log file parser.
This is extracting messages from TTCN3 component log files. 
Put the different component logs in correct order based on time stamps. 
Library makes conversion from ttcn3 message names to FMA message names. 
Finally it writes test case signalling flow in to the file.

Usage:
    ./{scriptname} sourcepath "casename|suffixnumb"
    
    sourcepath can be either resultdir in a local filesystem or url index page 
    that contains listing of files in the directory.
    
    sourcepath is expected to contain all component log files from ttcn 
    execution and the files should follow the naming rule:
    
    <testname>.TTCN3.<COMPONENT_NAME>.log
    
    for example:
    NS_9_0_0002 Guti Attach.TTCN3.ENB.log
    NS_9_0_0002 Guti Attach.TTCN3.SGW.log

"""

import sys
import os
import re
import urllib2
#import contextlib


class InterfaceSpec(object):

    interfaces = {
        'ENB': 's1',
        'ENB1': 's1',
        'ENB2': 's1',
        'ENB3': 's1',
        'ENB4': 's1',
        'ENB5': 's1',
        'HSS': 's6a',
        'DRA': 's6a',
        'DRA2': 's6a',
        'DRA3': 's6a',
        'DRA4': 's6a',
        'SGW': 's11',
        'SGW2': 's11',
        'SGSN': 'sgsn',
        'MME': 'mme',
        'MSC': 'sv',
        'CBC': 'sbc',
        'SGS': 'sgs',
        'RNC': 'iu',
        'RNC1': 'iu',
        'RNC2': 'iu',
        'RNC3': 'iu',
        'RNC4': 'iu',
        'BSC': 'gb',
        'BSC1': 'gb',
        'BSC2': 'gb',
        'BSC3': 'gb',
        'HLR' : 'gr',
        'VLR' : 'bssap',
        'VLR1' : 'bssap',
        'VLR2' : 'bssap',
        'VLR3' : 'bssap',
        'GGSN': 'gn',
        'GGSN1': 'gn',
        'GGSN2': 'gn',
        'SMLC': 'sls',
        'SMLC1': 'sls',
        'SMLC2': 'sls',
        'GMLC' : 's6',
        }
    messages = {
        's1': {
            'Initial UE Message (Attach Request)': 'attachRequest {.*pDNConnectivityRequest {',
            'Downlink NAS Transport (Authentication Request)': 'authenticationRequest {',
            'Uplink NAS Transport (Authentication Response)': 'authenticationResponse {',
            'Downlink NAS Transport (Security Mode Command)': 'securityModeCommand {',
            'Uplink NAS Transport (Security Mode Complete)': 'securityModeComplete {',
            'Initial Context Setup Request': 'InitialContextSetupRequest {(?!.*attachAccept {)(?!.*trackingAreaUpdateAccept {)',
            'Initial Context Setup Request (Attach Accept)': 'InitialContextSetupRequest {.*attachAccept {',
            'Initial Context Setup Request (TAU Accept)': 'tauAccept {',
            'Initial Context Setup Response': 'InitialContextSetupResponse {',
            'Uplink NAS Transport (Attach Complete)': 'attachComplete {',
            'UE Context Release Command': 'UEContextReleaseCommand {',
            'UE Context Release Complete': 'UEContextReleaseComplete {',
            'Uplink NAS Transport (Detach Request)': 'detachRequest {',
            'Downlink NAS Transport (Detach Request)': 'detachRequest {d',
            'Downlink NAS Transport (Detach Accept)': 'detachAccept {',
            'Uplink NAS Transport (Detach Accept)': 'detachAccept {u',
            'Downlink NAS Transport (Attach Reject)': 'attachReject {',
            'Uplink NAS Transport (Security Mode Reject)': 'securityModeReject {',
            'UE Context Release Request': 'UEContextReleaseRequest {',
            'Paging': 'Paging {',
            'Initial UE Message (Service Request)': 'serviceRequestMessage {',
            'Handover Request': 'HandoverRequest {',
            'Handover Request Acknowledge': 'HandoverRequestAcknowledge {',
            'Handover Command': 'HandoverCommand {',
            'Handover Notify': 'HandoverNotify {',
            'Uplink NAS Transport (Tracking Area Update Request)': 'trackingAreaUpdateRequest {',
            'Initial UE Message (Tracking Area Update Request)': 'trackingAreaUpdateRequest {i',
            'Downlink NAS Transport (Tracking Area Update Accept)': 'DownlinkNASTransport {.*trackingAreaUpdateAccept {',
            'Downlink NAS Transport (EMM Information)': 'DownlinkNASTransport {.*eMMInformation {',
            'Downlink NAS Transport (Identity Request)': 'DownlinkNASTransport {.*identityRequest {',
            'Initial Context Setup Request (Tracking Area Update Accept)': 'InitialContextSetupRequest {.*trackingAreaUpdateAccept',
            'Uplink NAS Transport (Tracking Area Update Complete)': 'trackingAreaUpdateComplete {',
            'Uplink NAS Transport (Identity Response)': 'identityResponse {',
            'Path Switch Request': 'PathSwitchRequest {',
            'Path Switch Request Acknowledge': 'PathSwitchRequestAcknowledge {',
            'Path Switch Request Failure': 'PathSwitchRequestFailure {',
            'E-RAB Setup Request (Activate Dedicated EPS Bearer Context Request)': 'activateDedicatedEPSBearerContextRequest {',
            'E-RAB Setup Response': 'S1AP.E_RABSetupResponse {',
            'Uplink NAS Transport (Activate Dedicated EPS Bearer Context Accept)': 'activateDedicatedEPSBearerContextAccept',
            'Uplink NAS Transport (Bearer Resource Allocation Request)': 'bearerResourceAllocationRequest {',
            'Uplink NAS Transport (Bearer Resource Modification Request)': 'bearerResourceModificationRequest {',
            'E-RAB Release Command (Deactivate EPS Bearer Context Request)': 'deactivateEPSBearerContextRequest {',
            'E-RAB Release Response': 'S1AP.E_RABReleaseResponse {',
            'Uplink NAS Transport (Deactivate EPS Bearer Context Accept)': 'deactivateEPSBearerContextAccept {',
            'Downlink NAS Transport (Service Reject)': 'serviceReject {',
            'Uplink NAS Transport (Activate Default EPS Bearer Context Accept)': 'S1AP.UplinkNASTransport {(?!.*attachComplete {).*activateDefaultEPSBearerContextAccept {',
            'Uplink NAS Transport (Activate Dedicated EPS Bearer Context Reject)': 'activateDedicatedEPSBearerContextReject {',
            'Uplink NAS Transport (PDN Connectivity Request)': 'S1AP.UplinkNASTransport {.*pDNConnectivityRequest {',
            'E-RAB Setup Request (Activate Default EPS Bearer Context Request)': 'S1AP.E_RABSetupRequest {.*activateDefaultEPSBearerContextRequest {',
            'E-RAB Modify Request (Modify EPS Bearer Context Request)': 'S1AP.E_RABModifyRequest {.*modifyEPSBearerContextRequest {',
            'Uplink NAS Transport (Activate Default EPS Bearer Context Reject)': 'activateDefaultEPSBearerContextReject {',
            'ENB Status Transfer': 'S1AP.ENBStatusTransfer {',
            'MME Status Transfer': 'S1AP.MMEStatusTransfer {',
            'Deactivate Trace': 'S1AP.DeactivateTrace {',
            'Trace Start': 'S1AP.TraceStart {',
            'Handover Required': 'S1AP.HandoverRequired {',
            'Handover Cancel': 'S1AP.HandoverCancel {',
            'Handover Cancel Acknowledge': 'S1AP.HandoverCancelAcknowledge {',
            'Handover Failure': 'S1AP.HandoverFailure {',
            'Handover Preparation Failure': 'S1AP.HandoverPreparationFailure {',
            'Downlink NAS Transport (Identity Request)': 'identityRequest {',
            'Uplink NAS Transport (Identity Response)': 'identityResponse {',
            'Write Replace Warning Request': 'WriteReplaceWarningRequest {',
            'Write Replace Warning Response': 'WriteReplaceWarningResponse {',
            'Kill Request': 'KillRequest {',
            'Kill Response': 'KillResponse {',
            'MME Direct Information Transfer': 'S1AP.MMEDirectInformationTransfer {',
            'eNB Direct Information Transfer': 'S1AP.ENBDirectInformationTransfer {',
            'Uplink NAS Transport (Extended Service Request)': 'extendedServiceRequest {',
            'UE Context Modification Request': 'S1AP.UEContextModificationRequest {',
            'UE Context Modification Response': 'S1AP.UEContextModificationResponse {',
            'Downlink Non UE-Associated LPPa Transport': 'S1AP.DownlinkNonUEAssociatedLPPaTransport {',
            'Uplink Non UE-Associated LPPa Transport': 'S1AP.UplinkNonUEAssociatedLPPaTransport {',
            'Downlink UE-Associated LPPa Transport': 'S1AP.DownlinkUEAssociatedLPPaTransport {',
            'Uplink UE-Associated LPPa Transport': 'S1AP.UplinkUEAssociatedLPPaTransport {',
            'Error Indication': 'S1AP.ErrorIndication {',
            'Downlink NAS Transport (ESM Information Request)': 'eSMInformationRequest {',
            'Uplink NAS Transport (ESM Information Response)': 'eSMInformationResponse {',
            'UE Capability Info Indication': 'S1AP.UECapabilityInfoIndication {',
            'Location Reporting Control': 'S1AP.LocationReportingControl {',
            'Location Report': 'S1AP.LocationReport {',
            'Downlink NAS Transport (Downlink Generic NAS Transport)': 'downlinkGenericNASTransport {',
            'Uplink NAS Transport (Uplink Generic NAS Transport)': 'uplinkGenericNASTransport {',
            'Downlink NAS Transport (CS Service Notification)': 'S1AP.DownlinkNASTransport {.*cSServiceNotification {',
            },
        's6a': {
            'Authentication Information Request': 'air {',
            'Authentication Information Answer': 'aia {',
            'Update Location Request': 'ulr {',
            'Update Location Answer': 'ula {',
            'Identity Check Request': 'ecr {',
            'Identity Check Answer': 'eca {',
            'Insert Subscriber Data Request': 'idr {',
            'Insert Subscriber Data Answer':' ida {',
            'Delete Subscriber Data Request': 'dsr {',
            'Delete Subscriber Data Answer': 'dsa {',
            'Purge UE Request': 'pur {',
            'Purge UE Answer': 'pua {',
            },
        's11': {
            'Create Session Request': 'createSessionRequest {',
            'Create Session Response': 'createSessionResponse {',
            'Modify Bearer Request': 'modifyBearerRequest {',
            'Modify Bearer Response': 'modifyBearerResponse {',
            'Delete Session Request': 'deleteSessionRequest {',
            'Delete Session Response': 'deleteSessionResponse {',
            'Release Access Bearer Request': 'releaseAccessBearersRequest {',
            'Release Access Bearer Response': 'releaseAccessBearersResponse {',
            'Downlink Data Notification': 'downlinkDataNtfcn {',
            'Downlink Data Notification Acknowledgement': 'downlinkDataNtfcnAck {',
            'Create Indirect Data Forwarding Tunnel Request': 'createIndirectDataForwardingTunnelReq {',
            'Create Indirect Data Forwarding Tunnel Response': 'createIndirectDataForwardingTunnelRes {',
            'Delete Indirect Data Forwarding Tunnel Request': 'deleteIndirectDataForwardingTunnelReq {',
            'Delete Indirect Data Forwarding Tunnel Response': 'deleteIndirectDataForwardingTunnelRes {',
            'Bearer Resource Command': 'bearerResourceCommand {',
            'Create Bearer Request': 'createBearerRequest {',
            'Create Bearer Response': 'createBearerResponse {',
            'Update Bearer Response': 'updateBearerResponse {',
            'Delete Bearer Request': 'deleteBearerRequest {',
            'Delete Bearer Response': 'deleteBearerResponse {',
            'Update Bearer Request': 'updateBearerRequest {',
            'Delete Bearer Command': 'deleteBearerCommand {',
            'Initial Context Setup Request (Modify EPS Bearer Context Request)': 'modifyEPSBearerContextRequest {',
            'Suspend Notification': 'suspendNotification {',
            'Suspend Acknowledge': 'suspendAcknowledge {',
            'Change Notification Request' : 'changeNotificationRequest { ',
            'Change Notification Response' : 'changeNotificationResponse {',
            },
        'sgsn': {
            'Forward Relocation Request': 'forwardRelocationRequest {',
            'Forward Relocation Response': 'forwardRelocationResponse {',
            'Forward Relocation Complete': 'forwardRelocationComplete {',
            'Forward Relocation Complete Acknowledge': 'forwardRelocationCompleteAcknowledge {',
            'Relocation Cancel Request': 'relocationCancelRequest {',
            'Relocation Cancel Response': 'relocationCancelResponse {',
            'SGSN Context Request': 'sgsnContextRequest {',
            'SGSN Context Response': 'sgsnContextResponse {',
            'SGSN Context Acknowledge': 'sgsnContextAcknowledge {',
            'Identification Request': 'identificationRequest {',
            'Identification Response': 'identificationResponse {',
            'RAN Information Relay (RIM)': 'ranInformationRelay {.*rimRoutingAddress {',
            },
        'mme': {
            'Forward Relocation Request': 'forwardRelocationRequest {',
            'Forward Relocation Response': 'forwardRelocationResponse {',
            'Forward Access Context Notification': 'forwardAccessContextNotification {',
            'Forward Access Context Acknowledge': 'forwardAccessContextAcknowledge {',
            'Forward Relocation Complete Notification': 'forwardRelocationCompleteNotification {',
            'Forward Relocation Complete Acknowledge': 'forwardRelocationCompleteAcknowledge {',
            'Relocation Cancel Request': 'relocationCancelRequest {',
            'Relocation Cancel Response': 'relocationCancelResponse {',
            'Context Request': 'contextRequest {',
            'Context Response': 'contextResponse {',
            'Context Acknowledge': 'contextAcknowledge {',
            'Identification Request': 'identificationRequest {',
            'Identification Response': 'identificationResponse {',
            },
        'sv': {
            'SRVCC PS to CS Request': 'srvccPs2CsRequest {',
            'SRVCC PS to CS Response': 'srvccPs2CsResponse {',
            'SRVCC PS to CS Complete Notification': 'srvccPs2CsCompleteNotification {',
            'SRVCC PS to CS Complete Acknowlege': 'srvccPs2CsCompleteAcknowledge {',
            'SRVCC PS to CS Cancel Notification': 'srvccPs2CsCancelNotification {',
            'SRVCC PS to CS Cancel Acknowledge': 'srvccPs2CsCancelAcknowledge {',   
            },
        'sbc': {
            'Write Replace Warning Request': 'Write_Replace_Warning_Request {',
            'Write Replace Warning Response': 'Write_Replace_Warning_Response {',
            'Stop Warning Request': 'Stop_Warning_Request {',
            'Stop Warning Response': 'Stop_Warning_Response {',
            },
        'sgs': {
            'SGsAP Location Update Request': 'location_update_request {',
            'SGsAP Location Update Reject': 'location_update_reject {',
            'SGsAP Location Update Accept': 'location_update_accept {',
            'SGsAP Imsi Detach Indication': 'imsi_detach_indication {',
            'SGsAP Imsi Detach Ack': 'imsi_detach_ack {',
            'SGsAP EPS Detach Indication': 'eps_detach_indication {',
            'SGsAP EPS Detach Ack': 'eps_detach_ack {',
            'SGsAP Paging Request': 'paging_request {',
            'SGsAP Paging Reject': 'paging_reject {',
            'SGsAP Service Request': 'service_request {',
            'SGsAP Alert Request': 'alert_request {',
            'SGsAP Alert Ack': 'alert_ack {',
            'SGsAP TMSI Reallocation Complete': 'tmsi_reallocation_complete {',
            'SGsAP Downlink Unitdata': 'downlink_unitdata {',
            'SGsAP Uplink Unitdata': 'uplink_unitdata {',
            'SGsAP Release Request': 'release_request {',
            'SGsAP Ue Unreachable': 'ue_unreachable {',
            },
        'gn': {
            'Create PDP Context Request': 'createPDPContextRequest {',
            'Create PDP Context Response': 'createPDPContextResponse {',
            'Update PDP Context Request': 'updatePDPContextRequest {',
            'Update PDP Context Response': 'updatePDPContextResponse {',
            'Delete PDP Context Request': 'deletePDPContextRequest {',
            'Delete PDP Context Response': 'deletePDPContextResponse {',
            },
        'gr': {
            'Authentication Information Request': 'MapSendAuthenticationInfoArg {',
            'Authentication Information Response': 'MapSendAuthenticationInfoRes {',
            'Location Update Request': 'MapUpdateGprsLocationArg {',
            'Location Update Response': 'MapInsertSubscriberDataArg {',
            'IMEI Check Request': 'MapCheckIMEIArgV2V1 {',
            'IMEI Check Response': 'MapCheckIMEIResV2V1 {',
            },
        'bssap': {
            'Location Update Request': 'location_update_request {',
            'Location Update Accept': 'location_update_accept {',
            'Paging Request': 'paging_request {',
            'GPRS Detach Indication': 'gprs_detach_indication {',
            'GPRS Detach Ack': 'gprs_detach_ack {',
            'Service Request': 'service_request {',
            },
        'iu': {
            'InitialUE (Attach Request)': 'attachRequest {',
            'InitialUE (Detach Request)': 'InitialUE_Message {.*detachRequest {',
            'InitialUE (Routing Area Update Request)': 'InitialUE_Message {.*routingAreaUpdateRequest {',
            'InitialUE (Service Request)': 'InitialUE_Message {.*serviceRequest {',
            'DirectTransfer (Authentication And Ciphering Request)': 'authenticationAndCipheringRequest {',
            'DirectTransfer (Authentication And Ciphering Response)': 'authenticationAndCipheringResponse {',
            'DirectTransfer (Identity Request)': 'identityRequest {',
            'DirectTransfer (Identity Response)': 'identityResponse {',
            'DirectTransfer (Attach Accept)': 'attachAccept {',
            'DirectTransfer (Attach Complete)': 'attachComplete {',
            'DirectTransfer (Attach Reject)': 'attachReject {',
            'DirectTransfer (Routing Area Update Request)': 'DirectTransfer {.*routingAreaUpdateRequest {',
            'DirectTransfer (Detach Request)': 'DirectTransfer {.*detachRequest {',
            'DirectTransfer (Detach Accept)': 'detachAccept {',
            'DirectTransfer (Detach Request)': 'detachRequest_N2M {',
            'DirectTransfer (Detach Accept)': 'detachAccept_M2N {',
            'DirectTransfer (Routing Area Update Accept)': 'routingAreaUpdateAccept {',
            'DirectTransfer (Routing Area Update Complete)': 'routingAreaUpdateComplete {',
            'DirectTransfer (Routing Area Update Reject)': 'routingAreaUpdateReject {',
            'DirectTransfer (Activate PDP Context Request)': 'activatePDPContextRequest {.*requestedNSAPI {',
            'DirectTransfer (Activate PDP Context Accept)': 'activatePDPContextAccept {.*negotiatedLLCSapi {',
            'DirectTransfer (Deactivate PDP Context Request)': 'deactivatePDPContextRequest {',	
            'DirectTransfer (Deactivate PDP Context Accept)': 'deactivatePDPContextAccept {',
            'DirectTransfer (Service Request)': 'DirectTransfer {.*serviceRequest {',
            'DirectTransfer (Service Accept)': 'serviceAccept {',
            'DirectTransfer (Modify PDP Context Request)': 'modifyPDPContextRequest_N2M {',
            'DirectTransfer (Modify PDP Context Request)': 'modifyPDPContextRequest_M2N {',
            'DirectTransfer (Modify PDP Context Accept)': 'modifyPDPContextAccept_M2N {',
            'DirectTransfer (Modify PDP Context Accept)': 'modifyPDPContextAccept_N2M {',
            'DirectTransfer (Modify PDP Context Reject)': 'modifyPDPContextReject {',
            'RANAP-PDU (Reset)': 'Reset {',
            'RANAP-PDU (ResetAcknowledge)': 'ResetAcknowledge {',
            'RANAP-PDU (CommonID)': 'CommonID {',
            'RANAP-PDU (Security Mode Command)': 'SecurityModeCommand {',
            'RANAP-PDU (Security Mode Complete)': 'SecurityModeComplete {',
            'RANAP-PDU (Rab Assignment Request)': 'RAB_AssignmentRequest {.*RAB_SetupOrModifyList {',
            'RANAP-PDU (Rab Assignment Response)': 'RAB_AssignmentResponse {.*RAB_SetupOrModifiedList {',
            'RANAP-PDU (Rab Assignment Release)': 'RAB_AssignmentRequest {.*RAB_ReleaseList {',
            'RANAP-PDU (Rab Assignment Release Response)': 'RAB_AssignmentResponse {.*RAB_ReleasedList {',
            'RANAP-PDU (IU Release Request)': 'Iu_ReleaseRequest {', 
            'RANAP-PDU (IU Release Command)': 'Iu_ReleaseCommand {', 
         	  'RANAP-PDU (IU Release Complete)': 'Iu_ReleaseComplete {', 
           	'RANAP-PDU (Relocation Required)': 'RelocationRequired {', 
           	'RANAP-PDU (Relocation Command)': 'RelocationCommand {', 
           	'RANAP-PDU (Forward SRNS Context)': 'ForwardSRNS_Context {', 
           	'RANAP-PDU (Relocation Request)': 'RelocationRequest {',
           	'RANAP-PDU (Relocation Request Acknowledge)': 'RelocationRequestAcknowledge {',	
           	'RANAP-PDU (Location Report)': 'LocationReportingControl {.*AreaIdentity {', 
            'RANAP-PDU (Location Reporting Control)': 'LocationReportingControl {.*RequestType {', 
            'RANAP-PDU (Paging)': 'Paging {',
           	},
         'gb': {
            'FLOW CONTROL BVC ': 'bssgpFlowControlBvc {',
            'FLOW CONTROL BVC ACK': 'bssgpFlowControlBvcAck {',
            'FLUSH LL': 'bssgpFlushLl {',
            'FLUSH LL ACK': 'bssgpFlushLlAck {',
            'PAGING PS': 'bssgpPagingPs {',
            'PAGING CS': 'bssgpPagingCs {',
            'SUSPEND': 'bssgpSuspend {',
            'SUSPEND ACK': 'bssgpSuspendAck {',	
            'RESUME': 'bssgpResume {',
            'RESUME ACK': 'bssgpResumeAck {',	
            'UL-UNITDATA (Attach Request)': 'attachRequest {',
            'UL-UNITDATA (Attach Complete)': 'attachComplete {',   
            'UL-UNITDATA (Activate PDP Context Request)': 'activatePDPContextRequest {.*requestedNSAPI {',    
            'UL-UNITDATA (Authentication And Ciphering Response)': 'authenticationAndCipheringResponse {',
            'UL-UNITDATA (Identity Response)': 'identityResponse {',
            'UL-UNITDATA (Routing Area Update Request)': 'routingAreaUpdateRequest {',
            'UL-UNITDATA (Routing Area Update Complete)': 'routingAreaUpdateComplete {',
            'UL-UNITDATA (XID)': 'bssgpulUnitdata {.*xid {',
            'UL-UNITDATA (Detach Request)': 'detachRequest {',
            'UL-UNITDATA (Modify PDP Context Request)': 'modifyPDPContextRequest_M2N {',
            'UL-UNITDATA (Modify PDP Context Accept)': 'modifyPDPContextAccept_M2N {',
            'DL-UNITDATA (Modify PDP Context Request)': 'modifyPDPContextRequest_N2M {',
            'DL-UNITDATA (Modify PDP Context Accept)': 'modifyPDPContextAccept_N2M {',
            'DL-UNITDATA (Modify PDP Context Reject)': 'modifyPDPContextReject {',
            'DL-UNITDATA (Attach Accept)': 'attachAccept {',
            'DL-UNITDATA (Activate PDP Context Accept)': 'activatePDPContextAccept {.*negotiatedLLCSapi {',
            'UL-UNITDATA (Deactivate PDP Context Request)': 'deactivatePDPContextRequest {',    
            'DL-UNITDATA (Deactivate PDP Context Accept)': 'deactivatePDPContextAccept {',
            'DL-UNITDATA (Routing Area Update Accept)': 'routingAreaUpdateAccept {',
            'DL-UNITDATA (XID)': 'bssgpDlUnitdata {.*xid {',
            'DL-UNITDATA (Detach Accept)': 'detachAccept {',
            'DL-UNITDATA (Authentication And Ciphering Request)': 'authenticationAndCipheringRequest {',
           	'DL-UNITDATA (Identity Request)': 'identityRequest {',
            'DL-UNITDATA (MT SMS)': 'rP_DATA_N2M {',
           	},
        'sls': {
            'Connectionless Information Message': 'LCSAP.Connectionless_Information {',           	
            'Connection Oriented Information' : 'LCSAP.Connection_Oriented_Information {',        
            'Location Request': 'LCSAP.Location_Request {',            
            'Location Response': 'LCSAP.Location_Response {',
            },
        's6': {
            'Provide Location Request': 'plr {',           	
            'Provide Location Answer' : 'pla {',
            'Location Report Request': 'lrr {',           	
            'Location Report Answer' : 'lra {',
            'Disconnect Peer Request': 'dpr {',           	
            'Disconnect Peer Answer' : 'dpa {',
            },
        }

    def compile_patterns(self):
        for data in self.messages.values():
            for key, pat in data.items():
                if isinstance(pat, basestring):
                    data[key] = re.compile(pat, re.DOTALL)


class RunlogParser(object):

    def __init__(self):
        self._components = {}
        self._messages = []

    def parse(self, components):
        self._components = components
        self._collect_messages_in_order()
        return self._messages

    def _collect_messages_in_order(self):
        for comp in self._components.values():
            self._messages += comp.grep_messages()
        self._messages.sort(key=lambda msg: msg.timestamp)


class ComponentLog(object):

    def __init__(self, content, component, msgpatterns):
        self._content = content
        self.component = component
        self.msgpatterns = msgpatterns
        self._messages = []
        self._msgpattern = self._compile_pattern()

    def _compile_pattern(self):
        return re.compile(r"""
                                            # line before the first line of decoded message
                                            # starts...
            \[(\d{2}:\d{2}:\d{2}.\d{3})]    #     timestamp (group1)
            \[.+]                           #     component
            ([sr].)                         #     direction (group2)
            .*                              #     rest of the line
            \r*\n                           #     line-feed
                                            # ...and finally ends
                                            
            \[.+]  \[.+]  vv\s              # first line of decoded message
            (Message:\s{                    #   message itself (group3)
            (?:.*\r*\n)*?                   #   non-greedy multiline anything matcher until...
            \[.+]  \[.+]  vv\s} \s*$        # ...in the last line decoded message ends
            )
            """, re.VERBOSE | re.MULTILINE)

    def grep_messages(self):
        #self._log('grepping SGW')
        for i in self._msgpattern.finditer(self._content):
            message = Message(self, *i.groups())
            #self._log('trying to identify: %s' % message._content)
            self._can_identify(message)
        return self._messages

    def _can_identify(self, msg):
        if msg.identify_message():
            #self._log('identified SGW message: %s' % msg.name)
            self._messages.append(msg)

#    def _log(self, msg):
#        if self.component == 'SGW':
#            print msg

class Message(object):

    def __init__(self, parent, timestamp, direction, content):
        self._parent = parent
        self._direction = self._set_direction(direction)
        self.timestamp = timestamp
        self._content = content
        self.name = ''

    def _set_direction(self, val):
        if val.startswith('s'):
            return 'send'
        elif val.startswith('r'):
            return 'receive'
        else:
            raise AssertionError('Message direction flag is ambiguous: %s' %val)

    def identify_message(self):
        candidates = []
        for name, msg_pattern in self._parent.msgpatterns.items():
            m = msg_pattern.search(self._content)
            if m:
                candidates.append(name)
        if len(candidates) == 1:
            self.name = candidates[0]
            return True
        elif len(candidates) > 1:
            raise AssertionError('Component log parsing error. Found several '
                                 'candidates %s for message:\n%s' % 
                                 (candidates, self._content))
        return False

    #def __str__(self):
    #    return self.msg_print(True)
    
    def _direction_arrow(self):
        return self._direction == 'send' and '------>' or '<------'

    def __str__(self):
        return self.msg_print(True, True)

    def msg_print(self, enable_timestamp, enable_ordersymbol=False):
        res = '| '
        #if enable_dots:
        #    res = '    ...  ' +res
        if enable_timestamp:
            res = '[%s]  ' %self.timestamp
        return res + '%-5s %s  SUT %s %s' % (
                self._parent.component +':', 
                self._direction_arrow(), 
                enable_ordersymbol and '-' or '  ',
                self.name)


class OpenComponentLogs(object):

    def __init__(self, path, ifspec):
        self._path = path
        self._ifspec = ifspec
        self._component_names = ifspec.interfaces.keys()
        self._available_logs = self._scan_testcases()

    def choose_testcase(self, testname=''):
        if not testname:
            testname = self._ask_testcase()
            print 'meni testname: %s' %str(testname)
        else:
            testname = tuple(testname.split('|'))
            print 'eimeni testname: %s' %str(testname)
        self.chosen_testname = testname
        print 'testname:', testname
        print 'available_logs keys: %s' %(self._available_logs[testname].keys())
        return self._available_logs[testname]

    def _ask_testcase(self):
        enum = list(enumerate([ tc for tc in sorted(self._available_logs) ]))
        choises = self._format_choises(enum)
        print choises
        while 1:
            sel = raw_input('select number: ')
            try:
                sel = int(sel)
                if 0 <= int(sel) - 1 <= len(self._available_logs) - 1:
                    return enum[sel - 1][1]
            except ValueError:
                pass
            print '\nSelect valid number! Please, try again ...'
            print choises

    def _format_choises(self, tclist):
        choises = ['%s)  %s %s' % (i + 1, urllib2.unquote(tc[0]), tc[1]) for i, tc in tclist]
        return '\nAvailable testlogs:\n%s\n' % ('\n'.join(choises))

    def _scan_testcases(self):
        if os.path.isdir(self._path):
            print 'source: local filesystem'
            opener = LocalfileOpener(self._path)
        else:
            print 'source: url download'
            opener = UrlOpener(self._path)
        return self._scan_sourcedir(opener)

    def _scan_sourcedir(self, opener):
        #from collections import defaultdict
        #res = defaultdict(dict)
        res = {}
        for filepath, tcname, component_name, logid in opener.scan_sourcedir(self._component_names):
            if (tcname, logid) not in res:
                res[(tcname, logid)] = {}
            print 'UPDATE: %s - %s' %((tcname, logid), component_name)
            res[(tcname, logid)].update(self._new_componentlog(
                opener.read_componentlog(filepath),
                component_name))
        print 'res: %s' %'\n'.join([ '%s: %s' % (k, v) for k, v in res.items()])
        return res

    def _new_componentlog(self, content, component_name):
        if_ = self._ifspec.interfaces[component_name]
        print 'new componentlog: %s' % component_name
        return {component_name: ComponentLog(content, component_name, self._ifspec.messages[if_])}


class BaseOpener(object):

    def __init__(self, filepath):
        self._basepath = filepath

class LocalfileOpener(BaseOpener):

    def read_componentlog(self, filename):
        f = open(os.path.join(self._basepath, filename))
        try:
            return f.read()
        finally:
            f.close()

    def scan_sourcedir(self, component_names):
        #pat = re.compile('(.*).TTCN3.(%s).log' % '|'.join(component_names))
        #pat = re.compile('(.*).(%s).(\d+).log' % '|'.join(component_names))
        pat = re.compile('(.*).TTCN3.(%s).(\d+).log' % '|'.join(component_names))
        for name in os.listdir(self._basepath):
            m = pat.match(name)
            if m:
                yield m.group(0), m.group(1), m.group(2), m.group(3)


class UrlOpener(BaseOpener):

    def read_componentlog(self, filename):
        return self._read_url(os.path.join(self._basepath, filename))

    def _read_url(self, path):
        try:
            f = urllib2.urlopen(path)
            return f.read().decode('utf-8')
        except IOError, e:
            print 'Tried to connect url: %s' %path
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print "The server couldn't fulfill the request."
                print 'Error code: ', e.code
        #finally:
        f.close()

    def scan_sourcedir(self, component_names):
        pattern = re.compile('href="((.*).TTCN3.(%s).log)"' % '|'.join(component_names))
        for m in pattern.finditer(self._read_url(self._basepath)):
            yield m.group(1), m.group(2), m.group(3)


class Writer(object):
    _template = """=== Message flow ===\n%s"""

    def __init__(self, source):
        self._source = source
        self._testname = source.chosen_testname[0]
        self._testid = source.chosen_testname[1]


class StdOutWriter(Writer):

    def _output(self, messages):
        ret = """
%s
%s
""" % (self._source.chosen_testname, '-' *79)
        return ret + self._template % '\n'.join(msg.msg_print(False, enable_ordersymbol=False) for msg in messages)

    def write(self, messages):
        print self._output(messages)


class TemplateWriter(Writer):

    def _writefile(self, filepath, content):
        f = open(filepath, 'w')
        try:
            f.write(content)
        finally:
            f.close()

    def write(self, messages, resultdir):
        content = self._file_content(messages)
        self._writefile(self._outpath(resultdir), content)

    def _file_content(self, messages):
        content = self._add_prefix(['=== Message flow ==='] + self.content(messages))
        return self._linebreak.join(content)

    def _add_prefix(self, content):
        return [self._lineprefix + c for c in content]

    def _outpath(self, resultdir):
        name = '%s.%s.%s.log' % (self._testname, self._fileaffix, self._testid)
        return os.path.join(resultdir, name)

class SrcTemplateWriter(TemplateWriter):
    _linebreak = '\n'
    _fileaffix = 'flowtemplate'
    _lineprefix = '    ...  '

    def content(self, messages):
        return [m.msg_print(False, enable_ordersymbol=True) for m in messages]

class RideTemplateWriter(TemplateWriter):
    _linebreak = '\r\n'
    _fileaffix = 'flowtemplate_ride'
    _lineprefix = ''

    def content(self, messages):
        return [m.msg_print(False, enable_ordersymbol=True) for m in messages]


def print_msc(resultdir, testname):
    runner = Runner(resultdir, testname)
    messages, _ = runner.parse()
    runner.write(messages)


class Runner(object):
    
    def __init__(self, resultdir, testname=''):
        self._resultdir = os.path.expanduser(resultdir)
        self._testname = testname

    def parse(self):
        os.environ["http_proxy"] = ''
        #urlpath = 'https://87.254.221.214/ci_log/adx/flexi_ns/N2_3_13_0/test_272712/Result/NS_2_0_0002/NS_0_0_0000/'
        #urlpath = 'http://10.102.125.102:8011/results/ns22/2012-11-16--1223/NS_70_7_0002/'
        #urlpath = 'http://10.102.125.102:8011/results/ns22/2012-11-16--1223/NS_9_0_0002/'

        ifspec = InterfaceSpec()
        ifspec.compile_patterns()

        self._source = OpenComponentLogs(self._resultdir, ifspec)
        component_logs = self._source.choose_testcase(self._testname)
        print 'component_logs keys: %s' % (component_logs.keys())
        messages = RunlogParser().parse(component_logs)
        return messages, self._source

    def write(self, messages):
        StdOutWriter(self._source).write(messages)
        SrcTemplateWriter(self._source).write(messages, self._resultdir)
        RideTemplateWriter(self._source).write(messages, self._resultdir)


if __name__ == '__main__':
    if 1 < len(sys.argv) < 4:
        print_msc(*sys.argv[1:])
    else:
        print ('1 mandatory arg (directory containing component logs or url).\n'
               '2nd optional arg testcase name.')

