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
package com.cognizant.devops.platformengine.message.factory;

import java.io.IOException;
import java.util.concurrent.TimeoutException;

import org.apache.log4j.Logger;

import com.cognizant.devops.platformcommons.config.ApplicationConfigProvider;
import com.cognizant.devops.platformcommons.config.MessageQueueDataModel;
import com.cognizant.devops.platformcommons.constants.MessageConstants;
import com.rabbitmq.client.AMQP;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;

public class MessageSubscriberFactory {
	private static final Logger log = Logger.getLogger(MessageSubscriberFactory.class);
	private ConnectionFactory factory;
	private Connection connection;
	private static MessageSubscriberFactory instance = new MessageSubscriberFactory(); 
	
	private void initConnectionFactory(){
		MessageQueueDataModel messageQueueConfig = ApplicationConfigProvider.getInstance().getMessageQueue();
		factory = new ConnectionFactory();
		factory.setHost(messageQueueConfig.getHost());
		factory.setUsername(messageQueueConfig.getUser());
		factory.setPassword(messageQueueConfig.getPassword());
		try {
			connection = factory.newConnection();
			Channel channel = connection.createChannel();
			channel.exchangeDeclare(MessageConstants.EXCHANGE_NAME, MessageConstants.EXCHANGE_TYPE, true);
			channel.close();
		} catch (IOException e) {
			log.error("Unable to create MQ connection", e);
		} catch (TimeoutException e) {
			log.error("Unable to create MQ connection within specified time.", e);
		}
	}

	private MessageSubscriberFactory(){
		initConnectionFactory();
	}
	
	public static MessageSubscriberFactory getInstance(){
		return instance;
	}
	
	private Connection getConnection() {
		MessageQueueDataModel messageQueueConfig = ApplicationConfigProvider.getInstance().getMessageQueue();
		if(factory == null) {
			factory = new ConnectionFactory();
			factory.setHost(messageQueueConfig.getHost());
			factory.setUsername(messageQueueConfig.getUser());
			factory.setPassword(messageQueueConfig.getPassword());
		}
		try {
			Connection connection = factory.newConnection();
			return connection;
		} catch (IOException e) {
			log.error("Unable to create MQ connection", e);
		} catch (TimeoutException e) {
			log.error("Unable to create MQ connection within specified time.", e);
		}
		return null;
	}
	
	public void registerSubscriber(String routingKey, final EngineSubscriberResponseHandler responseHandler) throws Exception {
		Channel channel = getConnection().createChannel();
		String queueName = routingKey.replace(".", "_");
		channel.queueDeclare(queueName, true, false, false, null);
		channel.queueBind(queueName, MessageConstants.EXCHANGE_NAME, routingKey);
		responseHandler.setChannel(channel);
		
		Consumer consumer = new DefaultConsumer(channel) {
			@Override
			public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties,
					byte[] body) throws IOException {
				responseHandler.handleDelivery(consumerTag, envelope, properties, body);
			}
		};
		channel.basicConsume(queueName, false, routingKey, consumer);
	}
	
	public void unregisterSubscriber(String routingKey, final EngineSubscriberResponseHandler responseHandler) throws IOException, TimeoutException{
		responseHandler.getChannel().basicCancel(routingKey);
		responseHandler.getChannel().close();
	}
}
