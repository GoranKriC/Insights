/*******************************************************************************
 * Copyright 2017 Cognizant Technology Solutions
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License.  You may obtain a copy
 * of the License at
 * 
 *   http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
 * License for the specific language governing permissions and limitations under
 * the License.
 ******************************************************************************/
package com.cognizant.devops.insights.maturity.app;

import org.apache.log4j.Logger;
import org.quartz.JobBuilder;
import org.quartz.JobDetail;
import org.quartz.Scheduler;
import org.quartz.SchedulerException;
import org.quartz.SimpleScheduleBuilder;
import org.quartz.Trigger;
import org.quartz.TriggerBuilder;
import org.quartz.impl.StdSchedulerFactory;

import com.cognizant.devops.insights.maturity.module.InsightsDevOpsMaturityModule;
import com.cognizant.devops.platformcommons.config.ApplicationConfigCache;
import com.cognizant.devops.platformcommons.config.ApplicationConfigProvider;


/**
 * Engine execution will start from Application. 1. Load the iSight config 2.
 * Initialize Publisher and subscriber modules 3. Initialize Correlation Module.
 */
public class Application {
	private static Logger log = Logger.getLogger(Application.class.getName());
	
	private static int defaultInterval = 600;
	private Application(){
		
	}
	
	public static void main(String[] args) {
		if(args.length > 0){
			defaultInterval = Integer.valueOf(args[0]);
		}

		// Load isight config
		ApplicationConfigCache.loadConfigCache();
		// Create Default users
		//new EngineUsersModule().onboardDefaultUsers();
		ApplicationConfigProvider.performSystemCheck();
		// Create correlation nodes
		//new EngineCorrelationNodeBuilderModule().initializeCorrelationNodes();
		
		// Subscribe for desired events.
		System.out.println("Coming here");
		JobDetail devopsMaturityJob = JobBuilder.newJob(InsightsDevOpsMaturityModule.class)
				.withIdentity("InsightsDevOpsMaturityModule", "iSight")
				.build();


		Trigger devopsMaturityTrigger = TriggerBuilder.newTrigger()
				.withIdentity("DevopsMaturityTriggerModuleTrigger", "iSight")
				.startNow()
				.withSchedule(SimpleScheduleBuilder.simpleSchedule()
						.withIntervalInSeconds(defaultInterval)
						.repeatForever())
				.build();

		// Tell quartz to schedule the job using our trigger
		Scheduler scheduler;
		try {
			System.out.println("Inside scheduler");
			scheduler = new StdSchedulerFactory().getScheduler();
			scheduler.start();
			scheduler.scheduleJob(devopsMaturityJob, devopsMaturityTrigger);
		} catch (SchedulerException e) {
			log.error(e);
		}
	}
	
}
